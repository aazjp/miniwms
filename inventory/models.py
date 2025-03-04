from django.db import models
# Create your models here.


class Inventory(models.Model):
   sku_id = models.CharField(max_length=16)
   stock = models.IntegerField()
   storage_location_id = models.CharField(max_length=16,null=True)
   name = models.CharField(max_length=16, null=True)
   color = models.CharField(max_length=16, null=True)
   size = models.CharField(max_length=16, null=True)
class Inventory_record(models.Model):
   sku_id = models.CharField(max_length=16)
   storage_location_id = models.CharField(max_length=16)
   quantity = models.IntegerField()
   create_time = models.DateTimeField(auto_now_add=True)
   operation_type = models.CharField(max_length=16)
   operator = models.CharField(max_length=16)
   
class storage_location(models.Model):
   id = models.AutoField(primary_key=True)
   location_name = models.CharField(max_length=16)
   location_address = models.CharField(max_length=16)