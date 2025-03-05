from django.shortcuts import render,redirect
from django.urls import reverse
import datetime
import logging
import sqlite3
from utils import exe_sql, exe_sql
from django.contrib import messages
import re
from utils import exe_sql_dict
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
# Create your views here.

def order_manage(request):
    if request.method == 'GET':
        base_sql = '''
        select 
            * 
            from 
                order_order oo
            left join 
                customer_customer cc
                on oo.customer_id = cc.id
                {}
                order by oo.date desc
        '''
        where_clause,params=(search_order(request))
        if where_clause:
            sub_sql = 'where '+' and '.join(where_clause)
            sql = base_sql.format(sub_sql)
            logging.debug(sql)
            order_list = exe_sql_dict(sql, params)
        else:
            sql = base_sql.format('')
            logging.debug(sql)
            order_list = exe_sql_dict(sql)
            
        customer_list_sql = '''
            select
                *
                from
                    customer_customer
                    '''
        customer_list = exe_sql(customer_list_sql)

        paginator = Paginator(order_list, 10)
        # 获取当前页码，默认为第 1 页
        page_number = request.GET.get('page')
        # 获取当前页的对象
        param_list = [f"{key}={value}" for key, value in request.GET.items() if key != 'page']
        param_str = '&'.join(param_list)
        page_obj = paginator.get_page(page_number)
        
        data = {
            'page_obj': page_obj,
            'customer_list': customer_list
        }
        return render(request, 'order/order_manage.html', data)


def order_add(request):
    # 生成订单号
    order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    if request.method == "GET":
        # 获取所有客户名称
        sql = ' select * from customer_customer'
        customer_list = exe_sql(sql)
        logging.debug(customer_list)
        data = {
            'customer_list':customer_list
        }
        return render(request, 'order/order_add.html',data)      
    if request.method == "POST":
        # 生成一个新订单并将客户id绑定
        customer_id = request.POST.get('customer_id')
        # 插入订单表
        sql = '''
        insert into 
            order_order
                (date,customer_id,status) 
            values
                (datetime('now'),?,0)
        '''
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql,[customer_id])
        return redirect(reverse('order:order_manage'))                                              
    
def validate_input(input_value):
    # 验证输入是否为字母和数字的组合
    pattern = r'^[a-zA-Z0-9]+$'
    return bool(re.match(pattern, input_value))

def check_stock(request,order_id):
    # 检查库存
    sql = '''
    SELECT 
        od.sku_id,
        od.sku_num, 
        COALESCE(SUM(inven.stock), 0) as total_stock
    FROM 
        order_orderdetail od
    LEFT JOIN 
        inventory_inventory inven
    ON
        od.sku_id = inven.sku_id
    WHERE 
        order_id = ?
    GROUP BY 
        od.sku_id, od.sku_num;
    '''
    sku_list = exe_sql(sql, [order_id])
    # 检查库存是否足够
    for sku in sku_list:
        sku_id = sku['sku_id']
        sku_num = sku['sku_num']
        total_stock = sku['total_stock']
        # 如果库存不足，则返回False
        if total_stock < sku_num:
            logging.error(f"商品 {sku_id} 库存不足，现有库存: {total_stock}，订单需求: {sku_num}")
            messages.error(request, f"商品 {sku_id} 库存不足，无法提交订单")
            return False
        # 如果库存为0，则返回False
        if total_stock == 0:
            logging.error(f"未找到商品 {sku_id} 的库存信息")
            messages.error(request, f"未找到商品 {sku_id} 的库存信息，无法提交订单")
            return False
    return True

# 出库商品
def update_stock(request,sku_list):
    try:
        # 循环订单中的每一个sku
        for sku in sku_list:
            sku_num = sku['sku_num']
            sku_id = sku['sku_id']

            # 查询该商品在各个库位的库存信息
            query_stock_sql = '''
            SELECT 
                storage_location_id, 
                stock
            FROM 
                inventory_inventory 
            WHERE 
                sku_id = ? 
            ORDER BY 
                stock ;
            '''
            stock_records = exe_sql(query_stock_sql, [sku_id])
            # 设置需要减去的库存数量
            remaining_quantity = sku_num
            # 对该sku的每条库存信息进行循环
            for record in stock_records:
                storage_location_id = record[0]
                available_stock = record[1]
                # 如果需要出库的sku数量为0，则跳出循环
                if remaining_quantity <= 0:
                    break

                # 计算本次从该库位扣除的数量
                # 如果该库位的库存小于等于需要扣除的数量，则扣除全部数量
                deduct_quantity = min(remaining_quantity, available_stock)
                logging.info(f"从库位 {storage_location_id} 扣除 {deduct_quantity} 个商品")
                # 
                if deduct_quantity > 0:
                    # 更新库存
                    update_stock_sql = '''
                    UPDATE 
                        inventory_inventory 
                    SET 
                        stock = stock - ? 
                    WHERE 
                        sku_id = ? AND storage_location_id = ?;
                    '''
                    exe_sql(update_stock_sql, [deduct_quantity, sku_id, storage_location_id])

                    # 插入库存记录
                    insert_record_sql = '''
                    INSERT INTO 
                        inventory_inventory_record
                        (
                            sku_id, 
                            storage_location_id, 
                            quantity,
                            create_time,
                            operation_type, 
                            operator)
                    VALUES 
                        (?,?,?,?,?,?);
                    '''
                    exe_sql(insert_record_sql,[sku_id, storage_location_id, deduct_quantity,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'订单出库', request.user.username])
                    # 更新需要扣除的库存数量
                    remaining_quantity -= deduct_quantity

            # if remaining_quantity > 0:
            #     # 如果遍历完所有库位后仍有剩余数量未扣除，说明库存不足
            #     logging.error(f"库存不足，商品 {sku_id} 仍需出库 {remaining_quantity} 件")
            #     messages.error(request, f"商品 {sku_id} 库存不足，无法完成出库")
            #     raise Exception("库存不足")

    except Exception as e:
        logging.error(f"Failed to update stock: {e}")
        messages.error(request, '更新商品库存失败')
        return False
    return True

# @transaction.atomic
def order_detail(request, order_id):
    if request.method == "GET":
        # 获取订单详情
        sql = '''
        SELECT 
            * 
        FROM 
            order_orderdetail 
        WHERE 
            order_id = ?;
        '''
        sku_list = exe_sql(sql, [order_id])
        # 计算订单总价
        total_price = calculate_total_price(order_id)

        data = {
            'order_detail_info': sku_list,
            'order_id': order_id,
            'total_price': total_price
        }
        return render(request, 'order/order_detail.html', data)

    if request.method == 'POST':
        # 检查订单状态
        check_status_sql = '''
        SELECT
            status
        FROM
            order_order
        WHERE
            order_id = ?
        '''
        status = exe_sql(check_status_sql, [order_id])[0]['status']
        if status == 1:
            messages.warning(request, '订单已结束,无法修改')
            return redirect('order:order_detail', order_id=order_id)
        # 如果是提交订单的请求
        if 'submit_order' in request.POST:
            # 检查库存是否充足
            if not check_stock(request,order_id):
                return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

            # 获取商品列表
            sql = '''
            SELECT 
                sku_num, 
                sku_price, 
                od.sku_id
            FROM 
                order_orderdetail od
            WHERE 
                order_id = ?;
            '''
            sku_list = exe_sql(sql, [order_id])

            # 出库商品
            if not update_stock(request,sku_list ):
                messages.warning(request, '出库失败')
                
                return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

            # 更新订单状态
            update_status_sql = '''
            UPDATE
                order_order
            SET 
                status = 1
            WHERE 
                order_id = ?
            '''
            try:
                exe_sql(update_status_sql, [order_id])
            except sqlite3.Error as e:
                logging.error(f"Failed to update order status: {e}")
                messages.error(request, '更新订单状态失败')
                return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

            # 更新订单总金额
            total_price = calculate_total_price(order_id)   
            update_total_price_sql = '''
            UPDATE 
                order_order 
            SET 
                total_price = ? 
            WHERE 
                order_id = ?;
            '''
            try:
                exe_sql(update_total_price_sql, [total_price, order_id])
            except sqlite3.Error as e:
                logging.error(f"Failed to update order total price: {e}")
                messages.error(request, '更新订单总金额失败')
                return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

            messages.success(request, '订单提交成功，总金额已更新，商品已出库')
            return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

        elif 'delete_item' in request.POST:
            sku_id = request.POST.get('sku_id')
            # 删除订单中的商品
            delete_sql = '''
            DELETE FROM 
                order_orderdetail 
            WHERE 
                order_id = ? 
            AND 
                sku_id = ?;
            '''
            try:
                exe_sql(delete_sql, [order_id, sku_id])
                messages.success(request, '商品删除成功')
            except sqlite3.Error as e:
                logging.error(f"Failed to delete item from order: {e}")
                messages.error(request, '删除商品失败')
            return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))
            
        # 添加商品
        sku_code_insert = request.POST.get('sku_code_insert')
        quantity_insert = request.POST.get('quantity_insert')
        if not quantity_insert:
            messages.error(request, '请输入商品数量')
            return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))
        if not validate_input(sku_code_insert):
            messages.error(request, '商品条码无效')
            return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

        # 查询条码是否存在
        check_sku = '''
        SELECT 
            * 
        FROM 
            style_sku 
        WHERE 
            id = ?;
        '''
        sku_info = exe_sql(check_sku, [sku_code_insert])

        if not sku_info:
            logging.debug('条码错误')
            messages.error(request, '条码错误')
            return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

        # 查询订单中是否有该商品
        sql = '''
        SELECT 
            * 
        FROM 
            order_orderdetail 
        WHERE 
            order_id = ? 
            AND 
            sku_id = ?;
        '''
        sku_list = exe_sql(sql, [order_id, sku_code_insert])

        if sku_list:
            # 更新商品数量
            update_order_detail = '''
            UPDATE 
                order_orderdetail 
            SET 
                sku_num = sku_num + ?
            WHERE 
                order_id = ? 
            AND 
                sku_id = ?;
            '''
            try:
                exe_sql(update_order_detail, [quantity_insert, order_id, sku_code_insert])
            except sqlite3.Error as e:
                logging.error(f"Failed to update order detail: {e}")
                messages.error(request, '更新订单详情失败')
                return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))
        else:
            # 获取商品价格
            get_price_sql = '''
            SELECT 
                price 
            FROM 
                style_sku sk
            LEFT JOIN 
                style_spu sp
            ON 
                sk.spu_id = sp.id
            WHERE 
                sk.id = ?;
            '''
            price_result = exe_sql(get_price_sql, [sku_code_insert])
            if price_result:
                price = price_result[0][0]
            else:
                price = 0

            # 插入商品
            insert_order_detail = '''
            INSERT INTO 
                order_orderdetail 
                    (
                        order_id,
                        sku_id,
                        sku_num,
                        sku_price
                    ) 
                VALUES 
                    (
                        ?,
                        ?,
                        ?,
                        ?
                    );
            '''
            try:
                exe_sql(insert_order_detail, [order_id, sku_code_insert, quantity_insert, price])
            except sqlite3.Error as e:
                logging.error(f"Failed to insert order detail: {e}")
                messages.error(request, '插入订单详情失败')
                return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))

        return redirect(reverse("order:order_detail", kwargs={'order_id': order_id}))
        
def calculate_total_price(order_id):
    sql = '''
    SELECT 
        SUM(sku_num * sku_price)
    FROM 
        order_orderdetail 
    WHERE 
        order_id = ?;
    '''
    result = exe_sql(sql, [order_id])
    return result[0][0] if result else 0

def search_order(request):
    where_clause = []
    params = []
    # order_id
    order_id = request.GET.get('order_id')
    if order_id:
        where_clause.append('order_id like ?')
        params.append(f'%{order_id}%')
        
    # create_time
    create_time_start = request.GET.get('create_time_start')
    create_time_end = request.GET.get('create_time_end')
    if create_time_start and create_time_end:
        where_clause.append('date BETWEEN ? AND ?')
        params.append(create_time_start)
        params.append(create_time_end)
    elif create_time_start:
        where_clause.append('date >= ?')
        params.append(create_time_start)
    elif create_time_end:
        where_clause.append('date <= ?')
        params.append(create_time_end)
        
    # customer_name
    customer_name = request.GET.getlist('customer_name')
    if customer_name:
        where_clause.append(f"name in ({','.join(['?'] * len(customer_name))})")
        params.extend(customer_name)
    # order_status
    order_status = request.GET.getlist('order_status')
    if order_status:
        where_clause.append(f"status in ({','.join(['?'] * len(order_status))})")
        params.extend(order_status)
    #total_price
    total_price_start = request.GET.get('total_price_start')
    total_price_end = request.GET.get('total_price_end')
    if total_price_start and total_price_end:
        where_clause.append('total_price BETWEEN ? AND ?')
        params.append(total_price_start)
        params.append(total_price_end)
    elif total_price_start:
        where_clause.append('total_price >= ?')
        params.append(total_price_start)
    elif total_price_end:
        where_clause.append('total_price <= ?')
        params.append(total_price_end)
    return where_clause, params
