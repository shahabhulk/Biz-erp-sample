from django.db import models


class VehicleBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    brand = models.ForeignKey(VehicleBrand, on_delete=models.PROTECT, related_name='models')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['brand__name', 'name']
        unique_together = [['brand', 'name']]

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class Vehicle(models.Model):
    customer = models.ForeignKey(
        'contacts.Customer',
        on_delete=models.PROTECT,
        related_name='vehicles',
    )
    brand = models.ForeignKey(VehicleBrand, on_delete=models.PROTECT)
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT)
    license_plate = models.CharField(max_length=20, blank=True, default='')
    chassis_number = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        plate = self.license_plate or '—'
        return f'{self.brand.name} {self.model.name} ({plate})'
