from . import views
from django.urls import path

app_name = "order"


urlpatterns = [
    path('order_manage', views.order_manage, name='order_manage'),
    path('order_add/', views.order_add, name='order_add'),
    path('order_detail/<order_id>/', views.order_detail, name='order_detail'),
    # path('search_order/', views.search_order, name='search_order'),
    
]