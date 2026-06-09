from django.contrib import admin
from .models import JobCard, ServiceDetailLine , Customer

# Register your models here.


class ServiceLineInline(admin.TabularInline):
    model = ServiceDetailLine
    extra = 1
    
    
@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ['sequence', 'customer', 'license_plate', 'vin', 'receipt_date', 'promised_date', 'assigned_to', 'state']
    list_filter = ['customer', 'state']
    search_fields = ['license_plate', 'vin']
    list_per_page = 10
    inlines = [ServiceLineInline]
    
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    search_fields = ['name', 'phone', 'email']
    list_per_page = 10