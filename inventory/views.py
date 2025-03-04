from utils import *
from django.core.paginator import Paginator
from django.shortcuts import render,redirect
from django.urls import reverse

def inventory(request):
    if request.method =='GET':
        base_sql = '''
        select 
                sk.*,
                sp.img as img,sp.cost,sp.price,sp.name,sp.remark,
                loc.location_name||':'||loc.location_address as storage_location,
                inven.stock
            from
                inventory_inventory inven
            left join
                style_sku sk 
                on inven.sku_id = sk.id 
            left join
                style_spu sp 
                on sk.spu_id = sp.id
            left join 
                inventory_storage_location loc
                on inven.storage_location_id = loc.id
                {}
        '''
        where_clause,params=(search_inventory(request))
        
        if where_clause:
            sub_sql = 'where '+' and '.join(where_clause)
            sql = base_sql.format(sub_sql)
            logging.debug(sql)
            logging.debug(params)
            inven_list = exe_sql_dict(sql, params)
        else:
            sql = base_sql.format('')
            logging.debug(sql)
            inven_list = exe_sql_dict(sql)
        paginator = Paginator(inven_list, 10)
        # 获取当前页码，默认为第 1 页
        page_number = request.GET.get('page')
        
        page_obj = paginator.get_page(page_number)
        sql = '''
        select * from inventory_storage_location
        '''
        loc_list = exe_sql(sql)
        data = {
            'page_obj': page_obj,
            'loc_list': loc_list,
            # 'param_str': param_str
        }
        return render(request, 'inventory/inventory.html',data)

def inventory_in(request):
    if request.method =='GET':
        sql = '''
        select* from inventory_storage_location
        '''
        storage_location_list = exe_sql(sql)
        data = {
            'storage_location_list': storage_location_list
        }
        return render(request, 'inventory/inventory_in.html',data)
    
    if request.method =='POST':
        sku_id = request.POST.get('sku_id').strip()
        # 检查sku_id是否存在
        sql = '''
        select * from style_sku where id = ?
        '''
        ret = exe_sql(sql,(sku_id,))
        # 如果不存在，返回错误信息
        if not ret:
            messages.error(request, 'sku_id不存在')
            return redirect(reverse('inventory:inventory_in'))
        sku = ret[0]
        storage_location_id = request.POST.get('storage_location_id')
        num = request.POST.get('num').strip()
        
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = '''
            UPDATE inventory_inventory
            SET stock = stock + ? 
            WHERE sku_id =? and storage_location_id = ?
            '''
            cursor.execute(sql,(num,sku_id,storage_location_id))
            if cursor.rowcount == 0:
                sql = '''
                INSERT INTO 
                inventory_inventory (sku_id,stock,storage_location_id,color,size) 
                VALUES (?,?,?,?,?)
                '''
                cursor.execute(sql,(sku['id'],num,storage_location_id,sku['color'],sku['size']))
        # 插入入库记录
        sql = '''
        INSERT INTO 
        inventory_inventory_record (sku_id,storage_location_id,quantity,create_time,operation_type,operator)
        values(?,?,?,?,?,?)
        '''
        exe_sql(sql,(sku_id,storage_location_id,num,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'扫码入库',request.user.username))
            
        messages.success(request,'入库成功')
        return redirect(reverse('inventory:inventory_in'))

def inventory_out(request):
    if request.method =='GET':
        sql = '''
        select* from inventory_storage_location
        '''
        storage_location_list = exe_sql(sql)
        data = {
            'storage_location_list': storage_location_list
        }
        return render(request, 'inventory/inventory_out.html',data)
    
    if request.method =='POST':
        sku_id = request.POST.get('sku_id')
        # 检查sku_id是否存在
        sql = '''
        select * from style_sku where id = ?
        '''
        ret = exe_sql(sql,(sku_id,))
        # 如果不存在，返回错误信息
        if not ret:
            messages.error(request, 'sku_id不存在')
            return redirect(reverse('inventory:inventory_out'))
        sku = ret[0]
        storage_location_id = request.POST.get('storage_location_id')
        num = request.POST.get('num')
        
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = '''
            select * from inventory_inventory where sku_id = ? and storage_location_id = ?'''
            ret = exe_sql(sql,(sku_id,storage_location_id))
            if ret[0]['stock']< int(num):
                messages.error(request, '库存不足')
                return redirect(reverse('inventory:inventory_out'))
            
            sql = '''
            UPDATE inventory_inventory
            SET stock = stock - ? 
            WHERE sku_id =? and storage_location_id = ?
            '''
            cursor.execute(sql,(num,sku_id,storage_location_id))
        # 插入出库记录
        sql = '''
        INSERT INTO 
        inventory_inventory_record (sku_id,storage_location_id,quantity,create_time,operation_type,operator)
        values(?,?,?,?,?,?)
        '''
        exe_sql(sql,(sku_id,storage_location_id,num,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'扫码出库',request.user.username))
        messages.success(request,'出库成功')
        return redirect(reverse('inventory:inventory_out'))
    
def inventory_record(request):
    if request.method == 'GET':
        base_sql = '''
        select iir.*,isl.location_name||':'||isl.location_address as location 
        from inventory_inventory_record iir
        left join inventory_storage_location isl
        on iir.storage_location_id = isl.id
        {}
        order by iir.create_time desc
        '''
        where_clause,params=(search_inventory_record(request))
        logging.debug(where_clause)
        if where_clause:
            sub_sql = 'where '+' and '.join(where_clause)
            sql = base_sql.format(sub_sql)
            logging.debug(sql)
            inventory_record = exe_sql_dict(sql, params)
        else:
            sql = base_sql.format('')
            logging.debug(sql)
            inventory_record = exe_sql_dict(sql)
            
        operator_list_sql = '''select username from main_userinfo'''
        operator_list = exe_sql(operator_list_sql)
        
        storage_location_list_sql = '''select id,location_name||':'||location_address as location from inventory_storage_location'''
        storage_location_list = exe_sql(storage_location_list_sql)
        
        paginator = Paginator(inventory_record, 20)
        # 获取当前页码，默认为第 1 页
        page_number = request.GET.get('page')
        # 获取当前页的对象
        # param_list = [f"{key}={value}" for key, value in request.GET.items() if key != 'page']
        # param_str = '&'.join(param_list)
        page_obj = paginator.get_page(page_number)
        data = {
            'page_obj':page_obj,
            'operator_list':operator_list,
            'storage_location_list':storage_location_list,
        }
        return render(request,'inventory/inventory_record.html',data)
    
def search_inventory(request):
    where_clause = []
    params = []
    stock_start = request.GET.get('stock_start')
    stock_end = request.GET.get('stock_end')
    if stock_start and stock_end:
        where_clause.append('stock between ? and ?')
        params.append(stock_start)
        params.append(stock_end)
    elif stock_start:
        where_clause.append('inven.stock >= ?')
        params.append(stock_start)
    elif stock_end:
        where_clause.append('inven.stock <= ?')
        params.append(stock_end)
    
    cost_start = request.GET.get('cost_start')
    cost_end = request.GET.get('cost_end')
    if cost_start and cost_end:
        where_clause.append('sp.cost between ? and ?')
        params.append(cost_start)
        params.append(cost_end)
    elif cost_start:
        where_clause.append('sp.cost >= ?')
        params.append(cost_start)
    elif cost_end:
        where_clause.append('sp.cost <= ?')
        params.append(cost_end)

    price_start = request.GET.get('price_start')
    price_end = request.GET.get('price_end')
    if price_start and price_end:
        where_clause.append('sp.price between ? and ?')
        params.append(price_start)
        params.append(price_end)
    elif price_start:
        where_clause.append('sp.price >= ?')
        params.append(price_start)
    elif price_end:
        where_clause.append('sp.price <= ?')
        params.append(price_end)
    
    
    storage_location = request.GET.get('storage_location')
    logging.info('storage_location: %s', storage_location)
    if storage_location:
        where_clause.append('loc.id = ?')
        params.append(storage_location)
    
    remark = request.GET.get('remark')
    if remark:
        where_clause.append('sp.remark like ?')
        params.append(f'%{remark}%')
    
    name = request.GET.get('name')
    if name:
        where_clause.append('sp.name like ?')
        params.append(f'%{name}%')
    
    
    sku_id = request.GET.get('sku_id')
    if sku_id:
        where_clause.append('sk.id like ?')
        params.append(f"%{sku_id.strip()}%")
        
    return where_clause, params

def search_inventory_record(request):
    where_clause = []
    params = []
    # sku_id
    sku_id = request.GET.get('sku_id')
    if sku_id :
        where_clause.append('iir.sku_id like ?')
        params.append(f'%{sku_id}%')

    # operation_type
    operation_type_list = request.GET.getlist('operation_type')
    logging.debug(operation_type_list)
    if operation_type_list:
        where_clause.append(f" operation_type in ({ ','.join(['?']*len(operation_type_list))})")
        params.extend(operation_type_list)
    # storage_location
    storage_location = request.GET.getlist('storage_location')
    if storage_location:
        where_clause.append(f"isl.id in ({ ','.join(['?']*len(storage_location))})")
        params.extend(storage_location)

    # operator
    operator = request.GET.getlist('operator')
    if operator:
        where_clause.append(f"operator in ({ ','.join(['?']*len(operator))})")
        params.extend(operator)
    
    # quantity
    quantity_start = request.GET.get('quantity_start')
    quantity_end = request.GET.get('quantity_end')
    if  quantity_start and quantity_end:
        where_clause.append('quantity between ? and ?')
        params.append(quantity_start)
        params.append(quantity_end)
    elif quantity_start:
        where_clause.append('quantity >= ?')
        params.append(quantity_start)
    elif quantity_end:
        where_clause.append('quantity <= ?')
        params.append(quantity_end)
        
    #create_time
    create_time_start = request.GET.get('create_time_start')
    create_time_end = request.GET.get('create_time_end')
    if  create_time_start and create_time_end:
        where_clause.append('create_time between ? and ?')
        params.append(create_time_start)
        params.append(create_time_end)
    elif create_time_start:
        where_clause.append('create_time >= ?')
        params.append(create_time_start)
    elif create_time_end:
        where_clause.append('create_time <= ?')
        params.append(create_time_end)
    return where_clause,params
        
        # base_sql = '''
        # select 
        #     iir.*,
        #     isl.location_name||':'||isl.location_address as location 
        # from 
        #     inventory_inventory_record iir
        # left join 
        #     inventory_storage_location isl
        # on 
        #     iir.storage_location_id = isl.id
        # {}
        # '''
           
        # if where_clause:
        #     sub_sql = ' where '+' and '.join(where_clause)
        #     sql = base_sql.format(sub_sql)
        #     logging.debug(sql)
        #     logging.debug(params)
        # else:
        #     sql = base_sql.format('')
        #     logging.debug(sql)
        #     logging.debug(params)
        # inventory_record = exe_sql_dict(sql, params)
        # operator_list_sql = '''
        # select username from main_userinfo
        # '''
        # operator_list = exe_sql(operator_list_sql)
        
        # storage_location_list_sql = '''
        # select id,location_name||':'||location_address as location from inventory_storage_location'''
        # storage_location_list = exe_sql(storage_location_list_sql)
        # # logging.debug(inven_list)
        
        # data   = {
        #     'inventory_record': inventory_record,
        #     'operator_list': operator_list,
        #     'storage_location_list': storage_location_list,
        # }
        # return render(request, 'inventory/inventory_record.html', data)

        
        