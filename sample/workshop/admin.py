from django.contrib import admin

from .models import JobCard, ServiceDetailLine


class ServiceLineInline(admin.TabularInline):
    model = ServiceDetailLine
    extra = 1


@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = [
        'sequence', 'customer', 'vehicle', 'odometer_km',
        'receipt_date', 'promised_date', 'assigned_to', 'state',
    ]
    list_filter = ['customer', 'state']
    search_fields = [
        'vehicle__license_plate',
        'vehicle__chassis_number',
        'sequence',
    ]
    list_per_page = 10
    inlines = [ServiceLineInline]
