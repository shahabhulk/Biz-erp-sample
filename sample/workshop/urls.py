from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='jobcard_list', permanent=False)),
    path('customers/', RedirectView.as_view(url='/contacts/customers/', permanent=True)),
    path('job-cards/', views.JobCardListView.as_view(), name='jobcard_list'),
    path('job-cards/new/', views.jobcard_create, name='jobcard_create'),
    path('job-cards/<int:pk>/edit/', views.jobcard_edit, name='jobcard_edit'),
]
