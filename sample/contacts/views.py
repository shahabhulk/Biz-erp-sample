import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView

from .forms import CustomerForm
from .models import Customer


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


class CustomerListView(ListView):
    model = Customer
    template_name = 'contacts/customer_list.html'
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

    return TemplateResponse(request, 'contacts/customer_form.html', {
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

    return TemplateResponse(request, 'contacts/customer_form.html', {
        'form': form,
        'title': customer.name,
        'customer': customer,
    })
