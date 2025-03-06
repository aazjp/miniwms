from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
import logging
from utils import *
from django.contrib import messages
import datetime
from miniwms.settings import MEDIA_URL
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required



def download_barcode(request, id):
    import miniwms.settings as settings
    barcode_dir = style_models.sku.objects.filter(id=id).first().barcode
    logging.info('founded barcode code')
    # try:
    img_dir =barcode_dir[1:]
    logging.info('barcode_dir:'+img_dir)
    r = HttpResponse(open(img_dir, "r"))
    logging.info('success opened:'+img_dir)
    r["content_type"] = "application/octet-stream"
    r["Content-Disposition"] = "attachment;filename=" + id + ".svg"
    return r

@permission_required('')
def style_manage(request):
    if request.method == 'GET':
        base_sql = '''
        SELECT 
        sp.*,group_concat(sk.color||' '||sk.size||' '||sk.id) as sku  
        FROM  style_sku sk 
        LEFT JOIN  style_spu sp 
        ON sp.id = sk.spu_id 
        {}
        GROUP BY sp.id;'''
        where_clause,params=search_spu(request)
        if where_clause:
            sub_sql = 'where '+' and '.join(where_clause)
            sql = base_sql.format(sub_sql)
            logging.debug(sql)
            spu_list = exe_sql_dict(sql, params)
        else:
            sql = base_sql.format('')
            logging.debug(sql)
            spu_list = exe_sql_dict(sql)
            
        for spu in spu_list:
            sku = spu['sku'].split(',')
            spu['sku'] = sku
        logging.debug(spu_list)
        paginator = Paginator(spu_list, 10)
        # 获取当前页码，默认为第 1 页
        page_number = request.GET.get('page')
        # # 获取当前页的对象
        page_obj = paginator.get_page(page_number)
        
        data = {
            'page_obj': page_obj,
            # 'param_str': param_str
        }
        return render(request, 'style/style_manage.html', data)

def style_add(request):
    if request.method == 'GET':
        id = auto_make_spu_code()
        data = {
            'id':id,
        }
        return render(request, 'style/style_add.html', data)
    if request.method == 'POST':
        # id
        id = request.POST.get('id')
        if not id:
            id = auto_make_spu_code()
        else:
            sql = "SELECT * FROM style_spu WHERE id = ?"
            spu_list = exe_sql(sql, [id])
            if spu_list:
                messages.error(request, 'id已存在')
                return redirect(reverse('style:style_add'))
        # color
        color = request.POST.get('color').strip()
        if not color:
            messages.error(request, 'color不能为空')
            return redirect(reverse('style:style_add'))
        # size
        size = request.POST.get('size').strip()
        if not size:
            messages.error(request, 'size不能为空')
            return redirect(reverse('style:style_add'))

        if not (check_color(request,color) and check_size(request,size)):
            return redirect('style:style_add')
        
        name = request.POST.get('name')  
        # img  
        img= request.FILES.get('img')
        logging.info(img)
        if img:
            img_dir =MEDIA_URL+ save_image_to_path(img,'style/spu/')
        else:
            img_dir = ''
        # season
        season = request.POST.get('season')
        # pattern_design
        pattern_design = request.POST.get('pattern_design')
        # design_source
        design_source = request.POST.get('design_source')
        cost = request.POST.get('cost')
        price = request.POST.get('price')
        # remark
        remark = request.POST.get('remark')
        
        create_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sql = "INSERT INTO style_spu (id,img,name,season,pattern_design,design_source,remark,create_date,update_date,cost,price) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
        params = (id,img_dir,name,season,pattern_design,design_source,remark,create_date,update_date,cost,price)
        exe_sql(sql,params)
        
        if sku_add(id,color,size):
            messages.success(request, '添加成功')
            return redirect(reverse('style:style_manage'))
        return redirect(reverse('style:style_add'))
    
def style_del(request,id):
    sql = "DELETE FROM style_sku WHERE spu_id = ?"
    exe_sql(sql,(id,))
    sql = "DELETE FROM style_spu WHERE id = ?"
    exe_sql(sql,(id,))
    return redirect(reverse('style:style_manage'))

def style_update(request,id):
    sql = "SELECT * FROM style_spu WHERE id = ?"
    spu = exe_sql(sql,(id,))
    if request.method == 'GET':
        sql = "SELECT * FROM style_spu WHERE id = ?"
        spu = exe_sql(sql,(id,))
        data  = {
            'spu':spu[0]
        }
        return render(request,'style/style_update.html',data)
    if request.method == 'POST':
        img = request.FILES.get('img')
        if img:
            img_dir =MEDIA_URL+ save_image_to_path(img,'style/spu/')
        else:
            img_dir = spu[0]['img']
        name = request.POST.get('name')
        season = request.POST.get('season')
        pattern_design = request.POST.get('pattern_design')
        design_source = request.POST.get('design_source')
        remark = request.POST.get('remark')
        price = request.POST.get('price')
        cost = request.POST.get('cost')
        update_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sql = '''
        UPDATE 
            style_spu 
        SET 
            img = ?,
            name = ?,
            season = ?,
            pattern_design = ?,
            design_source = ?,
            remark = ?,
            update_date = ? ,
            price = ?,
            cost = ?
        WHERE id = ?
        '''
        exe_sql(sql,(img_dir,name,season,pattern_design,design_source,remark,update_date,price,cost,id))
        
        return redirect(reverse('style:style_manage'))
    
def style_detail(request,id):
    sql = '''
    SELECT 
        sk.*,
        inven.stock,
        isl.location_name||':'||isl.location_address as location_name
    FROM 
        style_sku sk
    LEFT JOIN 
        inventory_Inventory inven 
        ON sk.id = inven.sku_id
    LEFT JOIN 
        inventory_storage_location isl 
        ON inven.storage_location_id = isl.id
    where spu_id = ?
    '''
    sku_list = exe_sql(sql,(id,))
    sql = "SELECT * FROM style_spu WHERE id = ?"
    spu = exe_sql(sql,(id,))[0]
    

    data = {
        'sku_list':sku_list,
        'spu':spu
    }
    return render(request,'style/style_detail.html',data)

def search_spu(request):
        where_clause = []
        params = []
        id = request.GET.get('id')
        if id:
            id = id.strip()
            where_clause.append('sp.id = ?')
            params.append(id)
        
        name = request.GET.get('name')
        if name:
            name = name.strip()
            where_clause.append('sp.name like ?')
            params.append(f'%{name}%')

        season = request.GET.get('season')
        if season:
            where_clause.append('sp.season = ?')
            params.append(season)

        # 成本价区间搜索
        cost_start= request.GET.get('cost_start')
        cost_end= request.GET.get('cost_end')
        if cost_start and cost_end:
            where_clause.append('sp.cost BETWEEN ? AND ?')
            params.append(cost_start)
            params.append(cost_end)
        elif cost_start:
            where_clause.append('sp.cost >= ?')        
            params.append(cost_start)    
        elif cost_end:
            where_clause.append('sp.cost <= ?')        
            params.append(cost_end)
        # 零售价区间搜索
        price_start= request.GET.get('price_start')
        price_end= request.GET.get('price_end')
        if price_start and price_end:
            where_clause.append('sp.price BETWEEN ? AND ?')
            params.append(price_start)
        elif price_start:
            where_clause.append('sp.price >= ?')        
            params.append(price_start)
        elif price_end:
            where_clause.append('sp.price <= ?')        
            params.append(price_end)
        # 创建日期
        create_date_start= request.GET.get('create_date_start')
        create_date_end= request.GET.get('create_date_end')
        if create_date_start and create_date_end:
            create_date_start= create_date_start
            create_date_end= create_date_end
            where_clause.append('sp.create_date BETWEEN ? AND ?')
            params.append(create_date_start)
            params.append(create_date_end)
        elif create_date_start:
            create_date_start= create_date_start
            logging.debug(create_date_start)
            where_clause.append('sp.create_date >= ?')
            params.append(create_date_start)    
        elif create_date_end:
            create_date_end= create_date_end
            where_clause.append('sp.create_date <= ?')        
            params.append(create_date_end)
        # 更新日期
        update_date_start= request.GET.get('update_date_start')
        update_date_end= request.GET.get('update_date_end')
        if update_date_start and update_date_end:
            where_clause.append('sp.update_date BETWEEN ? AND ?')
            params.append(update_date_start)
            params.append(update_date_end)
        elif update_date_start:
            where_clause.append('sp.update_date >= ?')        
            params.append(update_date_start)
        elif update_date_end:
            where_clause.append('sp.update_date <= ?')        
            params.append(update_date_end)
        
        return where_clause,params

def color_manage(request):
    if request.method == 'GET':
        base_sql = "SELECT * FROM style_color {} order by id desc"
        where_clause,params = search_color(request)
        if where_clause:
            sub_sql = 'where '+' and '.join(where_clause)
            sql = base_sql.format(sub_sql)
            logging.debug(sql)
            color_list = exe_sql_dict(sql, params)
        else:
            sql = base_sql.format('')
            logging.debug(sql)
            color_list = exe_sql_dict(sql)

        paginator = Paginator(color_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        data = {
            'page_obj': page_obj,
        }
        return render(request,'style/color_manage.html',data)
    if request.method == 'POST':
        id = request.POST.get('id')
        if len(id) != 3:
            messages.error(request,'颜色id必须为3位')
            return redirect(reverse('style:color_manage'))
        name = request.POST.get('name')
        if len(name) == 0:
            messages.error(request,'颜色名称不能为空')
            return redirect(reverse('style:color_manage'))  
        
        sql = "INSERT INTO style_color (id,name) VALUES (?,?)"
        exe_sql(sql,(id,name))
        return redirect(reverse('style:color_manage'))

def color_del(request,id):
    sql = "DELETE FROM style_color WHERE id = ?"
    exe_sql(sql,(id,))
    return redirect(reverse('style:color_manage'))

def search_color(request):
    where_clause =[]
    parmas = []
    color_id = request.GET.get('color_id')
    if color_id:
        where_clause.append("id like ?")
        parmas.append(f'%{color_id}%')
    color_name = request.GET.get('color_name')
    if color_name:
        where_clause.append("name like ?")
        parmas.append(f'%{color_name}%')
    return where_clause,parmas