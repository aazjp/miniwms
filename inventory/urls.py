from django.urls import include, path

from . import views

app_name='inventory'


urlpatterns = [
   path('inventory/',views.inventory,name='inventory'),
   path('inventory_in/',views.inventory_in,name='inventory_in'),
   path('inventory_out/',views.inventory_out,name='inventory_out'),
   path('inventory_record/',views.inventory_record,name='inventory_record'),
   # path('search_inventory/',views.search_inventory,name='search_inventory'),
   path('search_inventory_record/',views.search_inventory_record,name='search_inventory_record'),
]
