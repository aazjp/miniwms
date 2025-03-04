from django.db import models

# Create your models here.
class Customer(models.Model):
    id=models.CharField(primary_key=True,max_length=20)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, null=True, blank=True)
    remark = models.CharField(max_length=200, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)

    