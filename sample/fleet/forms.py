from django import forms

from .models import Vehicle, VehicleBrand, VehicleModel


class VehicleBrandForm(forms.ModelForm):
    class Meta:
        model = VehicleBrand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VehicleModelForm(forms.ModelForm):
    class Meta:
        model = VehicleModel
        fields = ['brand', 'name']
        widgets = {
            'brand': forms.Select(attrs={
                'class': 'form-select brand-autocomplete',
                'data-placeholder': 'Search or create brand...',
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['customer', 'brand', 'model', 'license_plate', 'chassis_number']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select customer-autocomplete',
                'data-placeholder': 'Search or select customer...',
            }),
            'brand': forms.Select(attrs={
                'class': 'form-select brand-autocomplete',
                'id': 'id_vehicle_brand',
                'data-placeholder': 'Search or create brand...',
            }),
            'model': forms.Select(attrs={
                'class': 'form-select model-autocomplete',
                'id': 'id_vehicle_model',
                'data-placeholder': 'Search or create model...',
                'data-brand-field': '#id_vehicle_brand',
            }),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        brand_id = None
        if self.data.get('brand'):
            brand_id = self.data.get('brand')
        elif self.instance.pk:
            brand_id = self.instance.brand_id

        if brand_id:
            self.fields['model'].queryset = VehicleModel.objects.filter(
                brand_id=brand_id,
            ).order_by('name')
        else:
            self.fields['model'].queryset = VehicleModel.objects.none()

    def clean(self):
        cleaned = super().clean()
        brand = cleaned.get('brand')
        model = cleaned.get('model')
        plate = (cleaned.get('license_plate') or '').strip()
        chassis = (cleaned.get('chassis_number') or '').strip()

        if brand and model and model.brand_id != brand.pk:
            self.add_error('model', 'Model does not belong to the selected car brand.')

        if not plate and not chassis:
            self.add_error(
                'license_plate',
                'Enter a license plate or chassis number.',
            )

        cleaned['license_plate'] = plate
        cleaned['chassis_number'] = chassis
        return cleaned
