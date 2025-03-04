import sqlite3
from style import models as style_models
import barcode
from django.shortcuts import  HttpResponse
import logging
from django.contrib import messages
import datetime
from  miniwms.settings import MEDIA_ROOT
import logging

def exe_sql(sql,params=None):
    try:
        with sqlite3.connect('db.sqlite3') as conn:
            if params:
                logging.debug(f"Executing SQL: {sql}, with params: {params}")
            else:
                logging.debug(f"Executing SQL: {sql}")
                
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if params:
                cursor.execute(sql,params)
            else:   
                cursor.execute(sql)
            return cursor.fetchall()
    except sqlite3.Error as e:
        # 回滚事务
        conn.rollback()
        # 记录详细的错误信息
        logging.error(f"数据库操作出错: {e}, SQL: {sql}, params: {params}")
        return []

def exe_sql_dict(sql, params=None):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql,params)
        else:   
            cursor.execute(sql)
            
        columns = [col[0] for col in cursor.description]
        
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

def auto_make_barcode(sku_code):
    barcode1 = barcode.get("code128", str(sku_code))  # 生成条形码
    barcode_filename = sku_code
    save_dir = 'media/style/barcode/'+barcode_filename
    barcode1.save(save_dir)  # 保存条形码
    return f"/{save_dir}.svg"

# 下载条形码
def download_barcode(request, style_code):
    import miniwms.settings as settings
    barcode_dir = style_models.Style.objects.filter(code=style_code).first().barcode
    logging.info('founded barcode code')
    # try:
    img_dir = settings.MEDIA_URL + str(barcode_dir)
    logging.info('barcode_dir:'+img_dir)
    r = HttpResponse(open(img_dir, "r"))
    logging.info('success opened:'+img_dir)
    r["content_type"] = "application/octet-stream"
    r["Content-Disposition"] = "attachment;filename=" + style_code + ".svg"
    return r

import os
import uuid

def save_image_to_path(image_file, save_to):
    """
    将图片保存到指定位置并返回保存后的路径。

    :param image_file: 图片文件对象（例如从 request.FILES 中获取的文件对象）
    :param save_directory: 图片要保存的目录
    :return: 保存后的图片文件路径，如果保存失败则返回 None
    """
    # 确保保存目录存在，如果不存在则创建
    # if not os.path.exists(save_to):
    #     os.makedirs(save_to)

    # 生成一个唯一的文件名，避免文件名冲突
    file_extension = os.path.splitext(image_file.name)[1]
    unique_filename = str(uuid.uuid4()) + file_extension
    save_path = save_to+unique_filename
    logging.info('save_path:'+save_path)

    try:
        # 以二进制写入模式打开文件并保存图片内容
        with open(os.path.join(MEDIA_ROOT,save_path), 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        return save_path
    except Exception as e:
        print(f"保存图片时出错: {e}")
        return None
    
def check_color(request,color):
    non_existent_colors=[]
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
    # 检查颜色是否都存在
        for c in color.split(' '):
            # 执行 SQL 查询
            cursor.execute("SELECT 1 FROM style_color WHERE name =?", (c,))
            # 获取查询结果
            result = cursor.fetchone()
            if not result:
                non_existent_colors.append(c)
        if non_existent_colors:
            messages.error(request, '颜色不存在: {}'.format(', '.join(non_existent_colors)))
            return False
    return True
        
def check_size(request,size):
    for s in size.split(' '):
        if s not in ["XS","S","M","L","XL","2XL"]:
            messages.error(request, '尺码错误: {}'.format(s))
            return False
    return True

def auto_make_spu_code():
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("select max(id) from style_spu where id like '%{}%'".format(datetime.datetime.now().strftime("%y%m%d") ))
        code = cursor.fetchone()[0]
        if code:
            return int(code)+1
        else:
            return int(datetime.datetime.now().strftime("%y%m%d")+"%03d"%1)

def sku_add(spu_id,color,size):
    for c in color.strip().split(' '):
        color_id = style_models.color.objects.filter(name=c).first().id
        if color_id.strip():
            for s in size.strip().split(' '):
                sku_id = str(spu_id) + color_id + s
                logging.debug(sku_id)
                barcode = auto_make_barcode(sku_id)
                style_models.sku.objects.create(id=sku_id ,spu_id=spu_id,color=c,size=s,barcode = barcode,create_date=datetime.datetime.now(), update_date=datetime.datetime.now())
    return True 