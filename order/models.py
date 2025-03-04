from django.db import models

# Create your models here.

# 订单表
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=1)
    total_price = models.FloatField(null=True)
    customer_id = models.CharField(max_length=10)
        
# 订单详细信息
class OrderDetail(models.Model):
    order_id = models.CharField(max_length=24)
    # 保存sku号
    sku_id=models.CharField(max_length=24)
    sku_num = models.IntegerField()
    # 保存sku价格
    sku_price = models.CharField( max_length=10)

