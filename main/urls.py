from django.contrib import admin
from django.urls import path,include
from . import views

app_name = 'main'

urlpatterns = [
    path('',views.login_view,name='login'),
    # path('login/',views.login_view,name='login_view'),
    # path('logined_base/',views.logined_base,name='logined_base'),
    path('logout/',views.logout_view,name='logout_view'),
    path('register/',views.register_view,name='register_view'),
    
]