from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.urls import reverse
from . import models
# pip install python-barcode
import barcode
import logging
import sqlite3
import xml.etree.ElementTree as ET
import make_barcode
from django.contrib import messages

# from barcode.writer import ImageWriter
# Create your views here.

def make_barcode_by_html(request, style_code):
    upload_dir = make_barcode.make_custom_barcode(style_code)
    sty = models.Style.objects.filter(code=style_code).first()
    sty.barcode=upload_dir+'.svg'
    sty.save()
    if request.method == "GET":
        return redirect(reverse("style:style_manage"))


# 创建时自动生成条形码
def auto_make_barcode(style_code):
    barcode1 = barcode.get("ean", str(style_code))  # 生成条形码
    dir = "barcode/" + str(style_code)
    save_dir='media/'+dir
    barcode1.save(save_dir)  # 保存条形码
    barcode_dir = dir + ".svg"
    return barcode_dir


# 下载条形码
def download_barcode(request, style_code):
    import miniwms.settings as settings
    barcode_dir = models.Style.objects.filter(code=style_code).first().barcode
    logging.info('founded barcode code')
    # try:
    img_dir = settings.MEDIA_URL + str(barcode_dir)
    logging.info('barcode_dir:'+img_dir)
    r = HttpResponse(open(img_dir, "r"))
    logging.info('success opened:'+img_dir)
    r["content_type"] = "application/octet-stream"
    r["Content-Disposition"] = "attachment;filename=" + style_code + ".svg"
    return r
    # except Exception:
    #     raise Http404("Download error")

# 款式管理
def style_manage(request):
    if request.method == "GET":
        # style_info = models.Style.objects.all()
        with sqlite3.connect("db.sqlite3") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("select * from style_style")
            style_info = cursor.fetchall()
        data={
            "style_info":style_info
        }
        return render(request, "style/style/style_manage.html",data)

# 添加款式
def style_add(request):
    data = {}
    if request.method == "POST":
        style_add_form = models.StyleAddForm(request.POST,request.FILES)
        
        # style_add_form.make_code()
        # if models.Style.objects.filter(code=style_add_form.instance.code):
        #     return HttpResponse("该款式已存在")
        if style_add_form.is_valid():
            logging.info("表单验证成功")
            style_add_form.make_code()
            # 如果不存在则保存
            if not models.Style.objects.filter(code=style_add_form.instance.code):
                style_add_form.save()
                return redirect(reverse("style:style_manage"))
            else:
                messages.error(request, "该款式已存在")
    style_add_form = models.StyleAddForm()
    data = {
        "style_add_form": style_add_form,
    }
    return render(request, "style/style/style_add.html", data)


# 删除款式
def style_delete(request, delete_id):
    models.Style.objects.filter(code=delete_id).delete()
    return redirect(reverse("style:style_manage"))


# 修改款式
def style_update(request, update_id):
    sty = models.Style.objects.filter(code=update_id).first()

    if request.method == "POST":
        style_update_form = models.StyleUpdateForm(request.POST,request.FILES, instance=sty)
        if style_update_form.is_valid():
            logging.info("表单验证成功")
            # 修改图片
            sty.img=request.FILES.get('img')
            style_update_form.save()
            return redirect(reverse("style:style_manage"))
    else:
        logging.info(sty)
        style_update_form = models.StyleUpdateForm(instance=sty)
        style_img = sty.img
        # logging.info(style_update_form)
    data = {"style_update_form": style_update_form, 
            "update_id": update_id,
            "style_img":style_img}
    return render(request, "style/style/style_update.html", data)


# 样式管理
def type_manage(request):
    if request.method == "GET":
        type_info = models.Type.objects.all()
        return render(request, "style/type/type_manage.html", {"type_info": type_info})


# 添加样式
def type_add(request):
    if request.method == "POST":
        type_add_form = models.TypeAddForm(request.POST)
        if type_add_form.is_valid():
            logging.info("表单验证成功")
            type_add_form.save()
            return redirect(reverse("style:type_manage"))
    else:
        type_add_form = models.TypeAddForm()
    data = {
        "type_add_form": type_add_form
    }
    return render(request, "style/type/type_add.html", data)


# 删除样式
def type_delete(request, delete_id):
    models.Type.objects.filter(code=delete_id).delete()
    return redirect(reverse("style:type_manage"))


# 修改样式
def type_update(request, update_id):
    type = models.Type.objects.filter(code=update_id).first()
    print(type)
    if request.method == "POST":
        type_update_form = models.TypeUpdateForm(request.POST, instance=type)
        if type_update_form.is_valid():
            logging.info("表单验证成功")
            type_update_form.save()
            return redirect(reverse("style:type_manage"))
    else:
        logging.info(type)
        type_update_form = models.TypeUpdateForm(instance=type)
        # logging.info(type_update_form)
    data = {"type_update_form": type_update_form, "update_id": update_id}
    return render(request, "style/type/type_update.html", data)


# 管理设计师
def designer_manage(request):
    if request.method == "GET":
        designer_info = models.Designer.objects.all()
        data = {
            "designer_info": designer_info
        }
        return render(request,"style/designer/designer_manage.html",data)


# 添加设计师
def designer_add(request):
    if request.method == "POST":
        designer_add_form = models.DesignerAddForm(request.POST)
        if designer_add_form.is_valid():
            logging.info("表单验证成功")
            designer_add_form.save()
            return redirect(reverse("style:designer_manage"))
    else:
        designer_add_form = models.DesignerAddForm()
    data = {
        "designer_add_form": designer_add_form
    }
    return render(request, "style/designer/designer_add.html", data)


# 删除设计师
def designer_delete(request, delete_id):
    models.Designer.objects.filter(code=delete_id).delete()
    return redirect(reverse("style:designer_manage"))


# 修改设计师
def designer_update(request, update_id):
    des = models.Designer.objects.filter(code=update_id).first()

    if request.method == "POST":
        designer_update_form = models.DesignerUpdateForm(request.POST, instance=des)
        if designer_update_form.is_valid():
            logging.info("表单验证成功")
            designer_update_form.save()
            return redirect(reverse("style:designer_manage"))
    else:
        logging.info(des)
        designer_update_form = models.DesignerUpdateForm(instance=des)
    data = {"designer_update_form": designer_update_form, "update_id": update_id}
    return render(request, "style/designer/designer_update.html", data)


# 管理颜色
def color_manage(request):
    if request.method == "GET":
        color_info = models.Color.objects.all()
        data = {
            "color_info": color_info
        }
        return render(request, "style/color/color_manage.html", data)

    if request.method == "POST":
        color_info = request.POST
        color = models.Color()
        color.color = color_info["color"]
        color.code = color_info["code"]
        color.save()
        return redirect(reverse("style:color_manage"))


# 删除颜色
def color_delete(request, delete_id):
    models.Color.objects.filter(code=delete_id).delete()
    return redirect(reverse("style:color_manage"))


# 修改颜色
def color_update(request, update_id):
    color = models.Color.objects.filter(code=update_id).first()

    if request.method == "POST":
        color_update_form = models.ColorUpdateForm(request.POST, instance=color)
        if color_update_form.is_valid():
            logging.info("表单验证成功")
            color_update_form.save()
            return redirect(reverse("style:color_manage"))
    else:
        logging.info(color)
        color_update_form = models.ColorUpdateForm(instance=color)
    data = {"color_update_form": color_update_form, "update_id": update_id}
    return render(request, "style/color/color_update.html", data)


# 添加颜色
def color_add(request):
    if request.method == "POST":
        color_add_form = models.ColorAddForm(request.POST)
        if color_add_form.is_valid():
            logging.info("表单验证成功")
            color_add_form.save()
            return redirect(reverse("style:color_manage"))
    else:
        color_add_form = models.ColorAddForm()
    data = {
        "color_add_form": color_add_form
    }
    return render(request, "style/color/color_add.html", data)
