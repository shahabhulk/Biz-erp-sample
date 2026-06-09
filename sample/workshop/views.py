import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView
from .models import JobCard, Customer
from .forms import JobCardForm, ServiceLineFormSet, CustomerForm


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


def _apply_customer_initial(form, request):
    customer_id = request.GET.get('customer')
    if not customer_id:
        return
    try:
        form.fields['customer'].initial = int(customer_id)
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
        'state_choices': JobCard.state_choices,
        'current_state': form['state'].value() or 'draft',
    }


# Create your views here.
class JobCardListView(ListView):
    model = JobCard
    template_name = 'workshop/jobcard_list.html'
    context_object_name = 'job_cards'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('customer', 'assigned_to')
        state = self.request.GET.get('state')
        if state:
            qs = qs.filter(state=state)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(sequence__icontains=q)
                | Q(customer__name__icontains=q)
                | Q(license_plate__icontains=q)
                | Q(vin__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_state'] = self.request.GET.get('state', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['state_choices'] = JobCard.state_choices
        return context
    
    
    
    
    
class CustomerListView(ListView):
    model = Customer
    template_name = 'workshop/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20


@require_GET
def customer_search(request):
    q = request.GET.get('q', '').strip()
    customers = Customer.objects.all()
    if q:
        customers = customers.filter(
            Q(name__icontains=q)
            | Q(phone__icontains=q)
            | Q(email__icontains=q)
        )
    customers = customers.order_by('name')[:15]
    return JsonResponse({
        'results': [{'id': c.pk, 'text': c.name} for c in customers],
    })


@require_POST
def customer_quick_create(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        name = payload.get('name', '').strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        name = request.POST.get('name', '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)

    existing = Customer.objects.filter(name__iexact=name).first()
    if existing:
        return JsonResponse({'id': existing.pk, 'text': existing.name})

    customer = Customer.objects.create(name=name)
    return JsonResponse({'id': customer.pk, 'text': customer.name})


def customer_create(request):
    next_url = _safe_next_url(request, request.GET.get('next'))

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            next_url = _safe_next_url(
                request,
                request.POST.get('next') or request.GET.get('next'),
            )
            if next_url:
                separator = '&' if '?' in next_url else '?'
                return redirect(f'{next_url}{separator}customer={customer.pk}')
            return redirect('customer_edit', pk=customer.pk)
    else:
        form = CustomerForm()

    return TemplateResponse(request, 'workshop/customer_form.html', {
        'form': form,
        'title': 'New Customer',
        'customer': None,
        'next_url': next_url,
    })


def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_edit', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return TemplateResponse(request, 'workshop/customer_form.html', {
        'form': form,
        'title': customer.name,
        'customer': customer,
    })
    
    
    

def jobcard_create(request):
    if request.method == 'POST':
        form = JobCardForm(request.POST)
        formset = ServiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            job_card = form.save()           # runs your sequence logic in save()
            formset.instance = job_card
            formset.save()
            return redirect('jobcard_edit', pk=job_card.pk)
    else:
        form = JobCardForm()
        _apply_customer_initial(form, request)
        formset = ServiceLineFormSet()
    return TemplateResponse(request, 'workshop/jobcard_form.html', _jobcard_form_context(
        request, form, formset, 'New Job Card', None,
    ))
    
    

def jobcard_edit(request, pk):
    job_card = get_object_or_404(JobCard, pk=pk)
    if request.method == 'POST':
        form = JobCardForm(request.POST, instance=job_card)
        formset = ServiceLineFormSet(request.POST, instance=job_card)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('jobcard_edit', pk=job_card.pk)
    else:
        form = JobCardForm(instance=job_card)
        _apply_customer_initial(form, request)
        formset = ServiceLineFormSet(instance=job_card)
    return TemplateResponse(request, 'workshop/jobcard_form.html', _jobcard_form_context(
        request, form, formset, f'Job Card {job_card.sequence}', job_card,
    ))