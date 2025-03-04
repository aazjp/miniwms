from django.db import models
import logging

# Create your models here.

class spu(models.Model):
    id=models.CharField(max_length=20,primary_key=True,null=False)
    name=models.CharField(max_length=20)
    img = models.ImageField(upload_to='style/spu',null=True)
    season=models.CharField(max_length=20,null=True)
    cost = models.FloatField(null=True)
    price = models.FloatField(null=True)
    pattern_design = models.CharField(max_length=20,null=True)
    design_source = models.CharField(max_length=20,null=True)
    remark = models.CharField(max_length=20,null=True)
    create_date=models.DateTimeField(null=True)
    update_date=models.DateTimeField(null=True)
    
class sku(models.Model):
    id=models.CharField(max_length=20,primary_key=True)
    spu_id = models.CharField(max_length=20)
    color=models.CharField(max_length=20)
    size=models.CharField(max_length=20)
    barcode=models.CharField(max_length=20,null=True)
    create_date=models.DateTimeField(null=True)
    update_date=models.DateTimeField(null=True)


class color(models.Model):
    id=models.CharField(max_length=20,primary_key=True)
    name=models.CharField(max_length=20)
    create_date=models.DateTimeField(null=True)
    update_date=models.DateTimeField(null=True)
    