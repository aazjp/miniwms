from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# 用户
class USERINFO(AbstractUser):
   username = models.CharField(primary_key=True,max_length=16, blank=False, unique=True,verbose_name="用户名")
   password = models.CharField(max_length=16, blank=False, verbose_name="密码")

