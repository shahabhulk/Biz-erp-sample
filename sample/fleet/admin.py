from django.contrib import admin

from .models import Vehicle, VehicleBrand, VehicleModel


@admin.register(VehicleBrand)
class VehicleBrandAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['brand', 'name']
    list_filter = ['brand']
    search_fields = ['name', 'brand__name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'brand', 'model', 'customer', 'chassis_number']
    list_filter = ['brand']
    search_fields = ['license_plate', 'chassis_number', 'customer__name']
