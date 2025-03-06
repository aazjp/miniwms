from django.contrib import admin
from .models import spu,sku,color

# Register your models here.
admin.site.register(spu)
admin.site.register(sku)
admin.site.register(color)