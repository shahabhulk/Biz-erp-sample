from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from fleet.models import Vehicle, VehicleBrand, VehicleModel

from .models import JobCard, ServiceDetailLine

DATETIME_PICKER_FORMAT = '%Y-%m-%d %H:%M'
DATETIME_PICKER_INPUT_FORMATS = [
    DATETIME_PICKER_FORMAT,
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%dT%H:%M:%S',
]


class LocalDateTimePickerWidget(forms.DateTimeInput):
    """Text input enhanced by Flatpickr (IST via Django TIME_ZONE)."""

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control datetime-picker',
            'autocomplete': 'off',
            'placeholder': 'Select date & time',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=DATETIME_PICKER_FORMAT)

    def format_value(self, value):
        if value is None:
            return ''
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime(self.format or DATETIME_PICKER_FORMAT)


class JobCardForm(forms.ModelForm):
    vehicle_brand = forms.ModelChoiceField(
        queryset=VehicleBrand.objects.all(),
        required=False,
        label='Car',
    )
    vehicle_model = forms.ModelChoiceField(
        queryset=VehicleModel.objects.none(),
        required=False,
        label='Model',
    )
    license_plate = forms.CharField(
        max_length=20,
        required=False,
        label='License Plate',
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_license_plate'}),
    )
    chassis_number = forms.CharField(
        max_length=50,
        required=False,
        label='Chassis Number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_chassis_number'}),
    )

    class Meta:
        model = JobCard
        fields = [
            'customer', 'vehicle', 'contact_name', 'odometer_km',
            'receipt_date', 'promised_date', 'assigned_to', 'state', 'notes',
        ]
        widgets = {
            'receipt_date': LocalDateTimePickerWidget(),
            'promised_date': LocalDateTimePickerWidget(),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'customer': forms.Select(attrs={
                'class': 'form-select customer-autocomplete',
                'data-placeholder': 'Search or create customer...',
            }),
            'vehicle': forms.Select(attrs={
                'class': 'form-select vehicle-autocomplete',
                'data-placeholder': 'Search existing vehicle...',
            }),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'odometer_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Odometer reading',
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].required = False
        self.fields['vehicle'].queryset = Vehicle.objects.select_related(
            'brand', 'model', 'customer',
        ).order_by('license_plate')

        for name in ('receipt_date', 'promised_date'):
            field = self.fields[name]
            field.input_formats = DATETIME_PICKER_INPUT_FORMATS
            field.widget.format = DATETIME_PICKER_FORMAT

        if not self.instance.pk and not self.is_bound:
            now = timezone.localtime()
            self.initial.setdefault('receipt_date', now)
            self.initial.setdefault('promised_date', now)

        brand_id = None
        if self.data.get('vehicle_brand'):
            brand_id = self.data.get('vehicle_brand')
        elif self.instance.pk and self.instance.vehicle_id:
            brand_id = self.instance.vehicle.brand_id

        if brand_id:
            self.fields['vehicle_model'].queryset = VehicleModel.objects.filter(
                brand_id=brand_id,
            ).order_by('name')

        customer_id = self.data.get('customer') or (
            self.instance.customer_id if self.instance.pk else None
        )
        if customer_id:
            self.fields['vehicle'].queryset = self.fields['vehicle'].queryset.filter(
                customer_id=customer_id,
            )

        if self.instance.pk and self.instance.vehicle_id:
            v = self.instance.vehicle
            self.fields['vehicle_brand'].initial = v.brand_id
            self.fields['vehicle_model'].initial = v.model_id
            self.fields['license_plate'].initial = v.license_plate
            self.fields['chassis_number'].initial = v.chassis_number

    def clean(self):
        cleaned = super().clean()
        customer = cleaned.get('customer')
        vehicle = cleaned.get('vehicle')
        brand = cleaned.get('vehicle_brand')
        model = cleaned.get('vehicle_model')
        plate = (cleaned.get('license_plate') or '').strip()
        chassis = (cleaned.get('chassis_number') or '').strip()

        if customer and vehicle and vehicle.customer_id != customer.pk:
            self.add_error('vehicle', 'This vehicle does not belong to the selected customer.')

        if not vehicle:
            if not brand:
                self.add_error('vehicle_brand', 'Car (brand) is required for a new vehicle.')
            if not model:
                self.add_error('vehicle_model', 'Model is required for a new vehicle.')
            if not plate and not chassis:
                self.add_error(
                    'license_plate',
                    'Enter a license plate or chassis number for a new vehicle.',
                )

        if brand and model and model.brand_id != brand.pk:
            self.add_error('vehicle_model', 'Model does not belong to the selected car brand.')

        cleaned['license_plate'] = plate
        cleaned['chassis_number'] = chassis
        return cleaned


ServiceLineFormSet = inlineformset_factory(
    JobCard,
    ServiceDetailLine,
    fields=('service_detail', 'service_type'),
    extra=1,
    can_delete=True,
    widgets={
        'service_detail': forms.TextInput(attrs={'class': 'form-control'}),
        'service_type': forms.TextInput(attrs={'class': 'form-control'}),
    }
)
