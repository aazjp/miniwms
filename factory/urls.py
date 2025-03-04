from . import views
from django.urls import path

app_name = "factory"


urlpatterns = [
    path('', views.factory, name='factory'),
]