from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PosTable, PosMenuItem, PosOrder, PosOrderItem

admin.site.register(PosTable)
admin.site.register(PosMenuItem)
admin.site.register(PosOrder)
admin.site.register(PosOrderItem)