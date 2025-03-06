from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from main.models import USERINFO as User
from django.contrib.auth import authenticate,login,logout
# from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from . import models
import barcode
import logging

# Create your views here.

# 登录
def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')
    if request.method == "POST":
        info = request.POST
        logging.info(info)
        user = authenticate(request=request,username = info['username'], password=info['password'])

        if user is not None:
            login(request=request,user=user)
            logging.info("登录成功")
            return redirect(reverse('index:index'))
        else:
            logging.info("登录失败")
            return redirect(reverse('main:login'))

# 登出
def logout_view(request):
    logout(request)
    logging.info("退出登录s")
    return redirect(reverse('main:login'))

# 注册
def register_view(request):
    if request.method == "GET":
        return render(request, 'register.html')
        
    if request.method == "POST":
        info = request.POST
        user = models.USERINFO.objects.filter(username=info['username'])
        if user:
            return render(request, 'register.html', {'msg': '用户名已存在'})
            
        else:
            user = models.USERINFO.objects.create_user(username=info['username'],password=info['password'])
            return render(request, 'register.html',{'msg':'注册成功'})