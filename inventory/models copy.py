from django.db import models
from sqlalchemy import true
from style.models import Style
# Create your models here.

# 库存
class INVENTORY(models.Model):
   id = models.AutoField(primary_key=True,  blank=False,  unique=True,  verbose_name="编号")
   style=models.ForeignKey(Style, on_delete=models.CASCADE,verbose_name="款式")       
   number = models.IntegerField(blank=False,verbose_name="数量")  
   remark = models.CharField(max_length=16, blank=True,  verbose_name="备注")
 
# 入库   
class INVENTORY_IN(models.Model):
   id = models.AutoField(primary_key=True,unique=True,verbose_name="编号") 
   style_name=models.CharField(max_length=16, blank=False,verbose_name="款式")
   style_code=models.CharField(max_length=16,blank=False,verbose_name="款号")
   style_size=models.CharField(max_length=16, blank=False,verbose_name="尺码")
   style_color=models.CharField(max_length=16,  blank=False,verbose_name="颜色")
   number = models.IntegerField(blank=False,verbose_name="数量")
   date=models.DateTimeField(auto_now_add=True,blank=True,  verbose_name="日期")
   remark = models.CharField(max_length=16,blank=True,verbose_name="备注")

# 出库
class INVENTORY_OUT(models.Model):
   id = models.AutoField(primary_key=True, unique=True)
   style_name=models.CharField(max_length=16)
   style_code=models.CharField(max_length=16)
   style_size=models.CharField(max_length=16)
   style_color=models.CharField(max_length=16)
   number = models.IntegerField()
   date=models.DateTimeField(auto_now_add=True,blank=True)
   remark = models.CharField(max_length=16)
