from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'workshop_customer'

    def __str__(self):
        return self.name
