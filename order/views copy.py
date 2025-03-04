from django.shortcuts import render,redirect
from django.urls import reverse
from . import models
import datetime
import logging
import sqlite3
# Create your views here.
def order_manage(request):
 
    order_info= models.Order.objects.raw('''
    select * from order_order
    left join customer_customer 
    on order_order.customer_id = customer_customer.id
    ''')
    print(order_info)
    data = {
        'order_info': order_info,
    }
    return render(request, 'order/order_manage.html', data)


def order_add(request):
    customer_info=models.Customer.objects.all()
    # 创建订单号
    order_code=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if request.method == 'POST' :
        logging.info('order_add')
        logging.info(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        # 创建订单对象
        order=models.Order.objects.create(
            code=order_code,
            customer_id=request.POST.get('customer_id'),
        )
        logging.info('订单新建成功')
        return redirect( reverse('order:order_detail', args=(order.code,)))
    if request.method == 'GET':
        data={
            'customer_info':customer_info ,
        }
        return render(request, 'order/order_add.html',data)
    
# 订单详情，购物车
# 扫描未登记的款式会崩溃
def order_detail(request, order_code):
    logging.info('order_detail')

    if request.method == 'GET':
        # 根据订单号查询库存情况，款式详情
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
        #    按照订单号查找购物车商品并连表查询价格，并自动计算库存是否充足
            sql=('''
            SELECT a.*, number as inven_num ,
                (SELECT case when a.sku_num<=number
                then '库存充足' ELSE '库存不足' END)as if_sufficient
            FROM 
                (SELECT 
                sku_code,sku_name,sku_detail,sku_num,price_cost,
                order_order.code AS order_code,style_style.id AS style_id
                FROM order_orderdetail 
                LEFT JOIN style_style,order_order
                ON style_style.code=order_orderdetail.sku_code
                AND order_order.id=order_orderdetail.order_id
                )a
            LEFT JOIN inventory_inventory 
            ON a.style_id=inventory_inventory.style_id
            WHERE order_code=$order_code;
            ''')
            cur.execute(sql,(order_code,))
            order_info = cur.fetchall()
        
        data={}
        if '库存不足' in [i['if_sufficient'] for i in order_info]:
            data['msg']='库存不足，无法结算订单'
        # 如果结算订单
        
        total_price=sum([int(i['price_cost'])*int(i['sku_num']) for i in order_info])
        data['order_code']=order_code
        data['total_price']=total_price
        data['order_info']=order_info
        
        return render(request, 'order/order_detail.html', data)
    
    
    if request.method == 'POST':
        info = request.POST
        # 获取款号
        sku_code_insert=info['sku_code_insert']
        print("扫码输入：",sku_code_insert)
      
        if len(sku_code_insert) != 12:   
            data = {
                'order_code':order_code ,
                'msg': '商品编码错误',
            }
            return render(request, 'order/order_detail.html', data)
        logging.info("款号正确")
      
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            sql=('''
                select case when EXISTS (
                SELECT sku_num from order_orderdetail
                where sku_code=$sku_code
                AND order_orderdetail.order_id=
                    (SELECT id from order_order where code=$order_code))
                then 1 else 0 end;''')
            cur.execute(sql,{
                'sku_code':sku_code_insert,
                'order_code':order_code,
            })
                
            if cur.fetchone()[0] :
                logging.info(sku_code_insert+'已存在')
                # 存在则数量加一
                sql=('''
                UPDATE order_orderdetail SET sku_num=sku_num+1
                where order_orderdetail.sku_code=$sku_code
                AND order_orderdetail.order_id=
                    (SELECT id from order_order where code=$order_code);
                ''')
                cur.execute(sql,{
                    'sku_code':sku_code_insert,
                    'order_code':order_code,
                })
                
            else:
                logging.info(sku_code_insert+'不存在,尝试创建')
                # 不存在则插入
                sql=('''
                INSERT into order_orderdetail(
                sku_code,sku_name,sku_detail,sku_num,order_id,sku_price)
                VALUES(
                    -- sku_code
                    $sku_code,
                    -- sku_name
                    (SELECT name  FROM style_style WHERE code=$sku_code),
                    -- sku_detail
                    (SELECT color||size FROM style_style 
                    LEFT JOIN style_color,style_size
                    ON style_style.color_id=style_color.code 
                    AND style_style.size_id=style_size.code
                    WHERE style_style.code=$sku_code),
                    -- sku_num
                    1,
                    -- order_id
                    (SELECT id from order_order where code=$order_code) ,
                    -- sku_price
                    0
                );
                ''')
                cur.execute(sql,{
                    'sku_code':sku_code_insert,
                    'order_code':order_code,
                })
                logging.info(sku_code_insert+'不存在,已创建')
        return redirect(reverse('order:order_detail', args=(order_code,)))
# 结算
# 商品价格 商品库存 订单号 库存数量
def order_submit(request,order_code):
    with sqlite3.connect('db.sqlite3') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql=('''
        SELECT sku_code,sku_num ,inven_num ,
            (SELECT case when sku_num<=inven_num
            then '库存充足' ELSE '库存不足' END
            ) as if_sufficient
        from order_orderdetail
        LEFT JOIN (
            SELECT style_style.code as sku_code1,
            inventory_inventory.number as inven_num
            from inventory_inventory
            LEFT JOIN style_style
            on inventory_inventory.style_id= style_style.id)
        on order_orderdetail.sku_code=sku_code1
        where order_orderdetail.order_id = 
        (
            SELECT id FROM order_order
            WHERE code = $order_code
        );
        ''')
        cur.execute(sql,(order_code,))
        order_info = cur.fetchall()
    # 检查订单中所有商品库存
    for i in order_info:
        # 如果有任何库存不足，则直接返回订单详情界面
        if i['if_sufficient']=='库存不足':
            logging.info(i['sku_code']+'库存不足')
            return redirect(reverse('order:order_detail', args=(order_code,)))

    # 如果库存充足
    logging.info('库存充足')
    # 修改订单状态为已提交
    with sqlite3.connect('db.sqlite3') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # 根据订单减少库存
        sql=('''
        UPDATE inventory_inventory set(number)=
        (
        number- 
        (
            SELECT sku_num from order_orderdetail
            LEFT JOIN style_style
            ON style_style.code=order_orderdetail.sku_code
            WHERE 
            order_orderdetail.order_id = 
                (
                    SELECT id FROM order_order
                    WHERE code = $order_code
                )
            AND 
            style_style.id=inventory_inventory.style_id
            )
        )
        where style_id=
        ( 
            SELECT style_style.id from order_orderdetail
            LEFT JOIN style_style
            ON style_style.code=order_orderdetail.sku_code
            WHERE 
            order_orderdetail.order_id = 
                (
                    SELECT id FROM order_order
                    WHERE code = $order_code
                )
            AND 
            style_style.id=inventory_inventory.style_id
        );
        ''')
        cur.execute(sql,(order_code,))
        # 修改订单状态为已提交
        sql=('''
        UPDATE order_order SET status=1
        WHERE code=$order_code;
        ''')
        cur.execute(sql,(order_code,))
        # 插入库存记录
        sql=('''
        INSERT into inventory_inventory_out(
            number,style_code,style_name,style_color,style_size,remark,date
        )
        SELECT sku_num,sku_code,name,color,size,'订单出库',datetime('now')
        from order_orderdetail
        LEFT JOIN style_style,style_color,style_size
        ON style_style.code=order_orderdetail.sku_code
        and style_color.code=style_style.color_id
        and style_size.code=style_style.size_id
        WHERE
        order_orderdetail.order_id =
            (
                SELECT id FROM order_order
                WHERE code = $order_code
            );
        ''')
        cur.execute(sql,(order_code,))
    return redirect(reverse('order:order_manage'))
                
            