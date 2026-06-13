from django.urls import path

from . import views

urlpatterns = [
    path('brands/', views.VehicleBrandListView.as_view(), name='brand_list'),
    path('brands/search/', views.brand_search, name='brand_search'),
    path('brands/quick-create/', views.brand_quick_create, name='brand_quick_create'),
    path('brands/new/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),

    path('models/', views.VehicleModelListView.as_view(), name='model_list'),
    path('models/search/', views.model_search, name='model_search'),
    path('models/quick-create/', views.model_quick_create, name='model_quick_create'),
    path('models/new/', views.model_create, name='model_create'),
    path('models/<int:pk>/edit/', views.model_edit, name='model_edit'),

    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/search/', views.vehicle_search, name='vehicle_search'),
    path('vehicles/models-by-brand/', views.models_by_brand, name='vehicle_models_by_brand'),
    path('vehicles/new/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/detail/', views.vehicle_detail, name='vehicle_detail'),
]
