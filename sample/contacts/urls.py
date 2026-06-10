from django.urls import path

from . import views

urlpatterns = [
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/search/', views.customer_search, name='customer_search'),
    path('customers/quick-create/', views.customer_quick_create, name='customer_quick_create'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
]
