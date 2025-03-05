from django.shortcuts import render,redirect
from django.urls import reverse
import datetime
from utils import exe_sql,exe_sql_dict
import logging
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.

def customer_manage(request):
    # 自动生成客户编号
    customer_id_add =datetime.datetime.now().strftime('%Y%m%d')+'%'
    sql = '''
        select max(id) as id from customer_customer 
        where id like ?
        '''
    param = (customer_id_add)
    customer_id_add = exe_sql(sql,[param])[0]['id']
    if customer_id_add:
            customer_id_add= str(int(customer_id_add)+1)
            logging.debug(customer_id_add)
    else:
        customer_id_add = "{}{}".format(datetime.datetime.now().strftime('%Y%m%d'),"001")

    logging.debug(customer_id_add)
    if request.method == 'GET':
        logging.debug(customer_id_add)
        base_sql = '''
        select 
            * 
        from 
            customer_customer
        {}
        '''
        
        where_clause,params=search_customer(request)
        if where_clause:
            sub_sql = 'where '+' and '.join(where_clause)
            sql = base_sql.format(sub_sql)
            logging.debug(sql)
            customer_info = exe_sql_dict(sql, params)
        else:
            sql = base_sql.format('')
            logging.debug(sql)
            customer_info = exe_sql_dict(sql)
        
        paginator = Paginator(customer_info, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        data = {
            'page_obj': page_obj,
            'customer_id_add':customer_id_add
        }
        return render(request, 'customer/customer_manage.html',data)
    if request.method == 'POST':
        id= request.POST.get('id')
        name = request.POST.get('name')
        if not name:
            messages.warning(request, '客户名称不能为空')
            return redirect('customer:customer_manage')
        
        phone = request.POST.get('phone')
        if not phone:
            messages.warning(request, '客户电话不能为空')
            return redirect('customer:customer_manage')
        
        email = request.POST.get('email')
        
        address = request.POST.get('address')
        remark = request.POST.get('remark')
        sql = '''
            insert into 
                customer_customer 
                    (
                        id,
                        name,
                        phone,
                        address,
                        create_time,
                        email,
                        remark
                    ) 
                values 
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        strftime('%Y-%m-%d','now'),
                        ?,
                        ?
                    )
                    '''
        if id:
            if len(id)!=11:
                messages.error(request, '客户编号必须为11位')
                return redirect(reverse('customer:customer_manage'))
            exe_sql(sql,[id,name,phone,address])
        else:
            exe_sql(sql,[customer_id_add,name,phone,address,email,remark])
        return redirect(reverse('customer:customer_manage'))
        
def customer_del(request,customer_id):
    if request.method == 'GET':
            exe_sql('''delete from customer_customer where id=?''',[customer_id])
            return redirect(reverse('customer:customer_manage'))

def customer_edit(request,customer_id):
    if request.method == 'GET':
        customer_info = exe_sql('''select * from customer_customer where id=?''',[customer_id])
        data = {
            'customer_info':customer_info[0]
        }
        return render(request,'customer\customer_edit.html',data)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        remark = request.POST.get('remark')

        update_parts = []
        params = []

        if name:
            update_parts.append("name = ?")
            params.append(name)
        if email:
            update_parts.append("email = ?")
            params.append(email)
        if phone:
            update_parts.append("phone = ?")
            params.append(phone)
        if address:
            update_parts.append("address = ?")
            params.append(address)
        if remark:
            update_parts.append("remark = ?")
            params.append(remark)
        if email:
            update_parts.append("email = ?")
            params.append(email)
        if update_parts:
            # 构建完整的 SQL 更新语句
            update_statement = ", ".join(update_parts)
            sql = f"UPDATE customer_customer SET {update_statement} WHERE id = ?"
            params.append(customer_id)

            # 执行 SQL 语句
            exe_sql(sql, params)
        
        return redirect(reverse('customer:customer_manage'))
    
def search_customer(request):
    where_clause = []
    params = []
    customer_id  = request.GET.get('customer_id')
    if customer_id:
        where_clause.append("id like ?")
        params.append(f'%{customer_id}%')
    
    customer_name = request.GET.get('customer_name')
    if customer_name:
        where_clause.append("name like ?")
        params.append(f'%{customer_name}%')
    
    customer_phone = request.GET.get('customer_phone')
    if customer_phone:
        where_clause.append("phone like ?")
        params.append(f'%{customer_phone}%')
    
    customer_address = request.GET.get('customer_address')
    if customer_address:
        where_clause.append("address like ?")
        params.append(f'%{customer_address}%')
    
    customer_email = request.GET.get('customer_email')
    if customer_email:
        where_clause.append("email like ?")
        params.append(f'%{customer_email}%')
    
    customer_remark = request.GET.get('customer_remark')
    if customer_remark:
        where_clause.append("remark like ?")
        params.append(f'%{customer_remark}%')
    
    
    return where_clause, params
    ...