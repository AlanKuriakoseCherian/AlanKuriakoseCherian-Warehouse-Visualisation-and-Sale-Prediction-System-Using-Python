import math
import pickle

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin, SingleObjectMixin

from .decorators import allowed_users
from .forms import ProductForm, OrderForm
from .models import Product, Order, DeliveryLog
import numpy as np

# Create your views here.


@login_required(login_url='user-login')
def index(request):
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    if request.user.is_superuser == False:
        order = order.filter(customer=request.user)
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.customer = request.user
                obj.save()
                return redirect('dashboard-index')
    else:
        form = OrderForm()
    context = {
        'form': form,
        'order': order[:15],
        'product': product,
        'product_count': product_count,
        'order_count': order_count,
        'customer_count': customer_count,
        'order_product_distribution_graph': Product.objects.annotate(request_count=Sum('order__order_quantity')).values(
            'name', 'request_count').order_by('-request_count'),
        'order_product_distribution_graph_amount_vice': Product.objects.annotate(
            request_count=F('mrp') * Sum('order__order_quantity')).values('name', 'request_count').order_by(
            '-request_count'),
        'del_log_qty':  DeliveryLog.objects.values('created_at__date').annotate(request_count=Sum('order__delivered_quantity')).order_by('-created_at__date')[:10],
        'del_log_amt':  DeliveryLog.objects.values('created_at__date').annotate(request_count=F('order__name__mrp')*Sum('order__delivered_quantity')).order_by('-created_at__date')[:10],
     }

    return render(request, 'dashboard/index.html', context)


@login_required(login_url='user-login')
def products(request):
    product = Product.objects.all()
    product_count = product.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    order = Order.objects.all()
    order_count = order.count()
    product_quantity = Product.objects.filter(name='')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            product_name = form.cleaned_data.get('name')
            messages.success(request, f'{product_name} has been added')
            return redirect('dashboard-products')
    else:
        form = ProductForm()
    context = {
        'product': product,
        'form': form,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
    }
    return render(request, 'dashboard/products.html', context)


@login_required(login_url='user-login')
def product_detail(request, pk):
    context = {

    }
    return render(request, 'dashboard/products_detail.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def customers(request):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    context = {
        'customer': customer,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
    }
    return render(request, 'dashboard/customers.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def customer_detail(request, pk):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customers = User.objects.get(id=pk)
    context = {
        'customers': customers,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,

    }
    return render(request, 'dashboard/customers_detail.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def product_edit(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=item)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Item{product.name} has been updated')
            return redirect('dashboard-products')
        messages.error(request, f'Please check the errors in the form')

    else:
        form = ProductForm(instance=item)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/products_edit.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def product_delete(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard-products')
    context = {
        'item': item
    }
    return render(request, 'dashboard/products_delete.html', context)


@login_required(login_url='user-login')
def order(request):
    page = int(request.GET.get('page', "1"))
    page_size = 25
    order = Order.objects.all().select_related('name', "customer")
    order_count = order.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()

    context = {
        'order': order[(page-1)*page_size:page*page_size],
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
    }

    if request.method == "POST":
        order_id = request.POST.get("order")
        qty = request.POST.get("delivered_quantity", 0)
        qty = int(qty)

        order_object_from_database = Order.objects.get(id=order_id)
        p = order_object_from_database.name
        s = order_object_from_database.order_quantity <= order_object_from_database.name.quantity
        if s:
            can_deliver = (
                                  order_object_from_database.order_quantity - order_object_from_database.delivered_quantity
                          ) >= qty
            if can_deliver:
                order_object_from_database.delivered_quantity = order_object_from_database.delivered_quantity + qty
                order_object_from_database.save()
                context[
                    'success'] = f"{qty} item has been marked as delivered against {order_object_from_database.name}"
                p.quantity = p.quantity - qty
                p.save()
                DeliveryLog.objects.create(
                    order=order_object_from_database,
                    quantity=qty,
                    created_by=request.user
                )
            else:
                error_m = "cannot deliver more than what is ordered"
                context["error"] = order_object_from_database.id
                context["error1"] = error_m
        else:
            error_s = "quantity ordered is not available"
            context["error"] = order_object_from_database.id
            context["error1"] = error_s
    context["no_pages"] = math.ceil(order_count / page_size)
    context["pages"] = range(1, context["no_pages"] + 1)
    context["page_number"] = page
    context["page_size"] = page_size
    context["add_index"] = (page - 1) * page_size
    return render(request, 'dashboard/order.html', context)


class OrderLogView(ListView):
    model = DeliveryLog
    template_name = 'dashboard/order_log_view.html'

    def queryset(self):
        return DeliveryLog.objects.filter(order_id=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['order'] = Order.objects.get(id=self.kwargs.get('pk'))
        return super(OrderLogView, self).get_context_data(object_list=object_list, **kwargs)


@login_required(login_url='user-login')
def result(request):
    cxt = {'result2': None, 'product_set': Product.objects.all().order_by('name').values('id', 'name')}
    try:
        product_id = int(request.GET['product'])
        year = int(request.GET['year'])
        month = int(request.GET['month'])
    except Exception as e:
        return render(request, "dashboard/predict.html", cxt)
    try:
        model = pickle.load(open(f'trained_data/SaleModel__{product_id}.pkl', 'rb'))
        pred = model.predict(np.array([month, year]).reshape(1, -1))
        pred = round(pred[0])
        price = f"Sale Prediction on {month, year} is  : Rs. {str(intcomma(pred))}"
        cxt['result2'] = price
    except FileNotFoundError as e:
        messages.warning(request, "Couldnot find Models for This Product. Please run 'python manage.py learn' to process learning.")
    return render(request, "dashboard/predict.html", cxt)


