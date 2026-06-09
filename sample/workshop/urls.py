from django.urls import path
from django.views.generic import RedirectView
from . import views


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='jobcard_list', permanent=False)),
    path('job-cards/', views.JobCardListView.as_view(), name='jobcard_list'),
    path('job-cards/new/', views.jobcard_create, name='jobcard_create'),
    path('job-cards/<int:pk>/edit/', views.jobcard_edit, name='jobcard_edit'),
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/search/', views.customer_search, name='customer_search'),
    path('customers/quick-create/', views.customer_quick_create, name='customer_quick_create'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    

]