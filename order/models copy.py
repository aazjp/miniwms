from django.db import models
from customer.models import Customer
from django.forms import ModelForm
import django.forms as forms
import datetime
from customer.models import Customer
from style.models import Style

# Create your models here.

# 订单表
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=24,unique=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=1)
    customer_id = models.CharField(max_length=10)
    total_price = models.CharField(max_length=10)

    # 订单保存时自动生成订单号
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
# 订单详细信息
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # 保存sku号
    sku_code=models.CharField(max_length=24)
    # 保存sku名字
    sku_name = models.CharField(max_length=24)
    # 保存sku详细信息
    sku_detail = models.CharField(max_length=24)
    # 保存sku数量
    sku_num = models.IntegerField()
    # 保存sku价格
    sku_price = models.CharField( max_length=10)
    # 待增加

    # 保存时自动计算sku总价
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)

# 添加订单表单
class OrderAddForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        exclude = ["status"]
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "readonly": True,
                }
            ),
            "date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "readonly": True,
                }
            ),
        }
        labels = {
            "code": "订单编号",
            "date": "日期",
            "customer_id": "客户",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["value"]= datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.fields["code"].widget.attrs["value"]= datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # 选择客户
        customer_choices = []
        customer_info=Customer.objects.all()
        for customer in customer_info:
            customer_choices.append((customer.id, customer.name))
        self.fields["customer_id"].widget= forms.Select(choices=customer_choices)