from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

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
    class Meta:
        model = JobCard
        fields = [
            'customer', 'contact_name', 'license_plate', 'vin',
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
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'vin': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('receipt_date', 'promised_date'):
            field = self.fields[name]
            field.input_formats = DATETIME_PICKER_INPUT_FORMATS
            field.widget.format = DATETIME_PICKER_FORMAT
        if not self.instance.pk and not self.is_bound:
            now = timezone.localtime()
            self.initial.setdefault('receipt_date', now)
            self.initial.setdefault('promised_date', now)


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
