from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth.decorators import login_required
app_name = 'style'


urlpatterns = [
    path('style_manage/', views.style_manage, name='style_manage'),
    path('style_add/', views.style_add, name='style_add'),
    path('style_del/<id>', views.style_del, name='style_del'),
    path('style_update/<id>', views.style_update, name='style_update'),
    path('style_detail/<id>', views.style_detail, name='style_detail'),
    # path('search_spu/', views.search_spu, name='search_spu'),
    path('download_barcode/<id>', views.download_barcode, name='download_barcode'),
    
    path('color_manage/', views.color_manage, name='color_manage'),
    path('color_del/<id>', views.color_del, name='color_del'),
]
