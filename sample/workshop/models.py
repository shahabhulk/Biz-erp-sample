from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(max_length=100, blank=True, default='')
    
    
    def __str__(self):
        return self.name
    
    
    
class JobCard(models.Model):
    state_choices=[('draft', 'Received'),
        ('diagnosis', 'In Diagnosis'),
        ('quote', 'Quotation Sent'),
        ('workorder', 'Work in Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')]
    
    
    sequence = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)   
    contact_name = models.CharField(max_length=100, blank=True) 
    license_plate = models.CharField(max_length=20, blank=True)
    vin = models.CharField(max_length=50, blank=True)
    receipt_date = models.DateTimeField()  # JC Date
    promised_date = models.DateTimeField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='1')
    state = models.CharField(max_length=20, choices=state_choices, default='draft')
    notes = models.TextField(blank=True)
    
    
    class Meta:
        ordering = ['-id'] 
        
        
    def __str__(self):
        return f"Job Card No: {self.sequence}"
    
    def save(self, *args, **kwargs):
        if not self.sequence:
            last = JobCard.objects.order_by('id').last()
            num = (int(last.sequence.split('-')[-1]) + 1) if last else 1
            self.sequence = f"JC-{num:05d}"
        super().save(*args, **kwargs)
        
        
class ServiceDetailLine(models.Model):
    job_card = models.ForeignKey(JobCard, on_delete=models.CASCADE)
    service_detail = models.CharField(max_length=100)
    service_type = models.CharField(max_length=100, blank=True)
    
    
    
           
    
      
    
    
    