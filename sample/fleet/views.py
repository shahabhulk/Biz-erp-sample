import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView

from .forms import VehicleBrandForm, VehicleForm, VehicleModelForm
from .models import Vehicle, VehicleBrand, VehicleModel


def _safe_next_url(request, next_url):
    if not next_url or not next_url.startswith('/'):
        return None
    if url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def _fleet_api_context():
    return {
        'brand_search_url': reverse('brand_search'),
        'brand_quick_create_url': reverse('brand_quick_create'),
        'model_search_url': reverse('model_search'),
        'model_quick_create_url': reverse('model_quick_create'),
        'customer_search_url': reverse('customer_search'),
        'customer_quick_create_url': reverse('customer_quick_create'),
    }


# ── Vehicle Brand ──────────────────────────────────────────────────────────

class VehicleBrandListView(LoginRequiredMixin, ListView):
    model = VehicleBrand
    template_name = 'fleet/brand_list.html'
    context_object_name = 'brands'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


@login_required
def brand_create(request):
    if request.method == 'POST':
        form = VehicleBrandForm(request.POST)
        if form.is_valid():
            brand = form.save()
            return redirect('brand_edit', pk=brand.pk)
    else:
        form = VehicleBrandForm()
    return TemplateResponse(request, 'fleet/brand_form.html', {
        'form': form,
        'title': 'New Car Brand',
        'brand': None,
    })


@login_required
def brand_edit(request, pk):
    brand = get_object_or_404(VehicleBrand, pk=pk)
    if request.method == 'POST':
        form = VehicleBrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('brand_edit', pk=brand.pk)
    else:
        form = VehicleBrandForm(instance=brand)
    return TemplateResponse(request, 'fleet/brand_form.html', {
        'form': form,
        'title': brand.name,
        'brand': brand,
    })


@login_required
@require_GET
def brand_search(request):
    q = request.GET.get('q', '').strip()
    brands = VehicleBrand.objects.all()
    if q:
        brands = brands.filter(name__icontains=q)
    brands = brands.order_by('name')[:15]
    return JsonResponse({
        'results': [{'id': b.pk, 'text': b.name} for b in brands],
    })


@login_required
@require_POST
def brand_quick_create(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        name = payload.get('name', '').strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        name = request.POST.get('name', '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)

    existing = VehicleBrand.objects.filter(name__iexact=name).first()
    if existing:
        return JsonResponse({'id': existing.pk, 'text': existing.name})

    brand = VehicleBrand.objects.create(name=name)
    return JsonResponse({'id': brand.pk, 'text': brand.name})


# ── Vehicle Model ──────────────────────────────────────────────────────────

class VehicleModelListView(LoginRequiredMixin, ListView):
    model = VehicleModel
    template_name = 'fleet/model_list.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('brand')
        q = self.request.GET.get('q', '').strip()
        brand_id = self.request.GET.get('brand')
        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(brand__name__icontains=q),
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_brand'] = self.request.GET.get('brand', '')
        context['brands'] = VehicleBrand.objects.order_by('name')
        return context


@login_required
def model_create(request):
    brand_id = request.GET.get('brand')
    if request.method == 'POST':
        form = VehicleModelForm(request.POST)
        if form.is_valid():
            model = form.save()
            return redirect('model_edit', pk=model.pk)
    else:
        form = VehicleModelForm()
        if brand_id:
            try:
                form.fields['brand'].initial = int(brand_id)
                form.fields['brand'].queryset = VehicleBrand.objects.all()
            except (ValueError, TypeError):
                pass

    ctx = {'form': form, 'title': 'New Vehicle Model', 'vehicle_model': None}
    ctx.update(_fleet_api_context())
    return TemplateResponse(request, 'fleet/model_form.html', ctx)


@login_required
def model_edit(request, pk):
    vehicle_model = get_object_or_404(VehicleModel, pk=pk)
    if request.method == 'POST':
        form = VehicleModelForm(request.POST, instance=vehicle_model)
        if form.is_valid():
            form.save()
            return redirect('model_edit', pk=vehicle_model.pk)
    else:
        form = VehicleModelForm(instance=vehicle_model)

    ctx = {'form': form, 'title': str(vehicle_model), 'vehicle_model': vehicle_model}
    ctx.update(_fleet_api_context())
    return TemplateResponse(request, 'fleet/model_form.html', ctx)


@login_required
@require_GET
def model_search(request):
    brand_id = request.GET.get('brand')
    q = request.GET.get('q', '').strip()
    models = VehicleModel.objects.select_related('brand')
    if brand_id:
        models = models.filter(brand_id=brand_id)
    if q:
        models = models.filter(name__icontains=q)
    models = models.order_by('name')[:15]
    return JsonResponse({
        'results': [{'id': m.pk, 'text': m.name} for m in models],
    })


@login_required
@require_POST
def model_quick_create(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        name = payload.get('name', '').strip()
        brand_id = payload.get('brand_id')
    except (json.JSONDecodeError, UnicodeDecodeError):
        name = request.POST.get('name', '').strip()
        brand_id = request.POST.get('brand_id')

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)
    if not brand_id:
        return JsonResponse({'error': 'Brand is required.'}, status=400)

    brand = get_object_or_404(VehicleBrand, pk=brand_id)
    existing = VehicleModel.objects.filter(brand=brand, name__iexact=name).first()
    if existing:
        return JsonResponse({'id': existing.pk, 'text': existing.name})

    vehicle_model = VehicleModel.objects.create(brand=brand, name=name)
    return JsonResponse({'id': vehicle_model.pk, 'text': vehicle_model.name})


# ── Vehicle ────────────────────────────────────────────────────────────────

class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'fleet/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('customer', 'brand', 'model')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(license_plate__icontains=q)
                | Q(chassis_number__icontains=q)
                | Q(customer__name__icontains=q)
                | Q(brand__name__icontains=q)
                | Q(model__name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


def _vehicle_form_context(request, form, title, vehicle, next_url=None):
    ctx = {
        'form': form,
        'title': title,
        'vehicle': vehicle,
        'next_url': next_url,
    }
    ctx.update(_fleet_api_context())
    return ctx


@login_required
def vehicle_create(request):
    next_url = _safe_next_url(request, request.GET.get('next'))
    customer_id = request.GET.get('customer')

    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            next_url = _safe_next_url(
                request,
                request.POST.get('next') or request.GET.get('next'),
            )
            if next_url:
                separator = '&' if '?' in next_url else '?'
                return redirect(f'{next_url}{separator}vehicle={vehicle.pk}')
            return redirect('vehicle_edit', pk=vehicle.pk)
    else:
        form = VehicleForm()
        if customer_id:
            try:
                form.fields['customer'].initial = int(customer_id)
            except (ValueError, TypeError):
                pass

    return TemplateResponse(request, 'fleet/vehicle_form.html', _vehicle_form_context(
        request, form, 'New Vehicle', None, next_url,
    ))


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('vehicle_edit', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)

    return TemplateResponse(request, 'fleet/vehicle_form.html', _vehicle_form_context(
        request, form, str(vehicle), vehicle,
    ))


@login_required
@require_GET
def vehicle_search(request):
    customer_id = request.GET.get('customer')
    q = request.GET.get('q', '').strip()

    vehicles = Vehicle.objects.select_related('brand', 'model', 'customer')
    if customer_id:
        vehicles = vehicles.filter(customer_id=customer_id)
    if q:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=q)
            | Q(chassis_number__icontains=q)
            | Q(brand__name__icontains=q)
            | Q(model__name__icontains=q)
        )
    vehicles = vehicles.order_by('license_plate')[:15]

    return JsonResponse({
        'results': [{'id': v.pk, 'text': str(v)} for v in vehicles],
    })


@login_required
@require_GET
def models_by_brand(request):
    brand_id = request.GET.get('brand')
    if not brand_id:
        return JsonResponse({'results': []})
    models = VehicleModel.objects.filter(brand_id=brand_id).order_by('name')
    return JsonResponse({
        'results': [{'id': m.pk, 'text': m.name} for m in models],
    })


@login_required
@require_GET
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(
        Vehicle.objects.select_related('brand', 'model'),
        pk=pk,
    )
    return JsonResponse({
        'id': vehicle.pk,
        'brand_id': vehicle.brand_id,
        'brand_name': vehicle.brand.name,
        'model_id': vehicle.model_id,
        'model_name': vehicle.model.name,
        'license_plate': vehicle.license_plate,
        'chassis_number': vehicle.chassis_number,
        'text': str(vehicle),
    })
