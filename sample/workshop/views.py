from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import ListView

from .forms import JobCardForm, ServiceLineFormSet
from .models import JobCard
from .services import resolve_vehicle_for_jobcard


def _apply_customer_initial(form, request):
    customer_id = request.GET.get('customer')
    if not customer_id:
        return
    try:
        form.fields['customer'].initial = int(customer_id)
    except (ValueError, TypeError):
        pass


def _apply_vehicle_initial(form, request):
    vehicle_id = request.GET.get('vehicle')
    if not vehicle_id:
        return
    try:
        form.fields['vehicle'].initial = int(vehicle_id)
    except (ValueError, TypeError):
        pass


def _jobcard_form_context(request, form, formset, title, job_card):
    return {
        'form': form,
        'formset': formset,
        'title': title,
        'job_card': job_card,
        'customer_search_url': reverse('customer_search'),
        'customer_quick_create_url': reverse('customer_quick_create'),
        'vehicle_search_url': reverse('vehicle_search'),
        'vehicle_detail_url': reverse('vehicle_detail', kwargs={'pk': 0}).replace('/0/', '/{id}/'),
        'brand_search_url': reverse('brand_search'),
        'brand_quick_create_url': reverse('brand_quick_create'),
        'model_search_url': reverse('model_search'),
        'model_quick_create_url': reverse('model_quick_create'),
        'state_choices': JobCard.state_choices,
        'current_state': form['state'].value() or 'draft',
    }


def _save_jobcard_from_form(form, formset):
    job_card = form.save(commit=False)
    vehicle = resolve_vehicle_for_jobcard(
        customer=form.cleaned_data['customer'],
        vehicle=form.cleaned_data.get('vehicle'),
        brand=form.cleaned_data.get('vehicle_brand'),
        model=form.cleaned_data.get('vehicle_model'),
        license_plate=form.cleaned_data.get('license_plate', ''),
        chassis_number=form.cleaned_data.get('chassis_number', ''),
    )
    job_card.vehicle = vehicle
    job_card.save()
    formset.instance = job_card
    formset.save()
    return job_card


class JobCardListView(LoginRequiredMixin, ListView):
    model = JobCard
    template_name = 'workshop/jobcard_list.html'
    context_object_name = 'job_cards'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'customer', 'assigned_to', 'vehicle', 'vehicle__brand', 'vehicle__model',
        )
        state = self.request.GET.get('state')
        if state:
            qs = qs.filter(state=state)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(sequence__icontains=q)
                | Q(customer__name__icontains=q)
                | Q(vehicle__license_plate__icontains=q)
                | Q(vehicle__chassis_number__icontains=q)
                | Q(vehicle__brand__name__icontains=q)
                | Q(vehicle__model__name__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_state'] = self.request.GET.get('state', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['state_choices'] = JobCard.state_choices
        return context


@login_required
def jobcard_create(request):
    if request.method == 'POST':
        form = JobCardForm(request.POST)
        formset = ServiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            job_card = _save_jobcard_from_form(form, formset)
            return redirect('jobcard_edit', pk=job_card.pk)
    else:
        form = JobCardForm()
        _apply_customer_initial(form, request)
        _apply_vehicle_initial(form, request)
        formset = ServiceLineFormSet()
    return TemplateResponse(request, 'workshop/jobcard_form.html', _jobcard_form_context(
        request, form, formset, 'New Job Card', None,
    ))


@login_required
def jobcard_edit(request, pk):
    job_card = get_object_or_404(JobCard, pk=pk)
    if request.method == 'POST':
        form = JobCardForm(request.POST, instance=job_card)
        formset = ServiceLineFormSet(request.POST, instance=job_card)
        if form.is_valid() and formset.is_valid():
            _save_jobcard_from_form(form, formset)
            return redirect('jobcard_edit', pk=job_card.pk)
    else:
        form = JobCardForm(instance=job_card)
        _apply_customer_initial(form, request)
        _apply_vehicle_initial(form, request)
        formset = ServiceLineFormSet(instance=job_card)
    return TemplateResponse(request, 'workshop/jobcard_form.html', _jobcard_form_context(
        request, form, formset, f'Job Card {job_card.sequence}', job_card,
    ))
