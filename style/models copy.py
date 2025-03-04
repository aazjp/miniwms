from calendar import c
from tkinter import Widget
from django.db import models
from django.forms import ModelForm, Select, Textarea, TextInput
from django import forms
import logging
from .views import auto_make_barcode


# Create your models here.
# 颜色
class Color(models.Model):
    code = models.CharField(
        primary_key=True, unique=True, max_length=3, blank=True, verbose_name="编号"
    )
    color = models.CharField(max_length=16, blank=True, verbose_name="颜色")

    def __str__(self) -> str:
        return self.code + " " + self.color


# 尺寸
class Size(models.Model):
    code = models.CharField(
        primary_key=True, unique=True, max_length=2, blank=True, verbose_name="编号"
    )
    size = models.CharField(max_length=4, blank=True, verbose_name="尺码")

    def __str__(self) -> str:
        return self.code + " " + self.size


# 设计师
class Designer(models.Model):
    code = models.CharField(
        primary_key=True, unique=True, max_length=2, blank=True, verbose_name="编号"
    )
    name = models.CharField(max_length=16, blank=True, verbose_name="设计师")

    def __str__(self) -> str:
        return self.code + " " + self.name


# 样式
class Type(models.Model):
    code = models.CharField(
        primary_key=True, unique=True, max_length=5, blank=True, verbose_name="编号"
    )
    name = models.CharField(max_length=16, blank=True, verbose_name="样式")

    def __str__(self) -> str:
        return self.code + " " + self.name


# 款式编号=商品编号（5）+设计师（2）+颜色（3）+尺码（2）
# 款式
class Style(models.Model):
    code = models.CharField(
        max_length=12, blank=True, unique=True, verbose_name="款式编号"
    )
    barcode = models.ImageField(
        upload_to="barcode/", blank=True, verbose_name="条形码"
    )
    name = models.CharField(max_length=16, verbose_name="名称")
    designer = models.ForeignKey(
        Designer, on_delete=models.CASCADE, verbose_name="设计师"
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, verbose_name="颜色")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="尺码")
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name="类型")
    img = models.ImageField(upload_to="style",blank=True, verbose_name="图片")
    price_cost = models.CharField(max_length=6, blank=True, verbose_name="成本价")
    price_retail = models.CharField(
        max_length=6, blank=True, verbose_name="零售价")
    price_wholesale = models.CharField(
        max_length=6, blank=True, verbose_name="批发价")
    remark = models.CharField(max_length=2048, blank=True, verbose_name="备注")

# 添加style的表单


class StyleAddForm(ModelForm):
    class Meta:
        model = Style
        fields = "__all__"
        # exclude = ["barcode"]
        widgets = {
            "code": TextInput(
                attrs={
                    "readonly": True,
                    "placeholder": "自动生成",
                }
            ),
            "remark": Textarea(
                attrs={
                })
        }

    def make_code(self):
        self.instance.code = "{}{}{}{}".format(
            self.instance.type.code,
            self.instance.designer.code,
            self.instance.color.code,
            self.instance.size.code,    
    )

    def save(self, commit: bool = ...):
        # self.instance.code = "{}{}{}{}".format(
        #     self.instance.type.code,
        #     self.instance.designer.code,
        #     self.instance.color.code,
        #     self.instance.size.code,
        # )
        self.instance.barcode = auto_make_barcode(self.instance.code)
        logging.info("正在保存" + self.instance.code)
        logging.info("正在保存" + self.instance.code)
        self.instance.save()
        logging.info("=====================================")
        logging.info("保存成功")
        super().save(commit)

    def __init__(self, *args, **kwargs):
        super(StyleAddForm, self).__init__(*args, **kwargs)

# 修改style的表单


class StyleUpdateForm(ModelForm):
    class Meta:
        model = Style
        fields = [
            "code",
            "name",
            "price_cost",
            "price_retail",
            "price_wholesale",
            "remark",
        ]

    def __init__(self, *args, **kwargs):
        super(StyleUpdateForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['readonly'] = True



class ColorAddForm(ModelForm):
    class Meta:
        model = Color
        fields = "__all__"
    def __init__(self, *args, **kwargs):
            super(ColorAddForm, self).__init__(*args, **kwargs)
            self.fields['code'].widget.attrs['placeholder'] = "三位数字"

class DesignerAddForm(ModelForm):
    class Meta:
        model = Designer
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super(DesignerAddForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['placeholder'] = "两位数字"


class TypeAddForm(ModelForm):
    class Meta:
        model = Type
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super(TypeAddForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['placeholder'] = "五位数字"


class ColorUpdateForm(ModelForm):
    class Meta:
        model = Color
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super(ColorUpdateForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['readonly'] = True



class DesignerUpdateForm(ModelForm):
    class Meta:
        model = Designer
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super(DesignerUpdateForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['readonly'] = True



        
class TypeUpdateForm(ModelForm):
    class Meta:
        model = Type
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super(TypeUpdateForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['readonly'] = True