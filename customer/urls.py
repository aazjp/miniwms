from . import views
from django.urls import path

app_name = "customer"


urlpatterns = [
    path('customer_manage/', views.customer_manage, name='customer_manage'),
    path('customer_del/<customer_id>', views.customer_del, name='customer_del'),
    path('customer_edit/<customer_id>', views.customer_edit, name='customer_edit'),
]