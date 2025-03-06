from django.contrib import admin
from .models import Inventory, Inventory_record, storage_location

admin.site.register(Inventory)
admin.site.register(Inventory_record)
admin.site.register(storage_location)
# Register your models here.
