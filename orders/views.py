from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from orders.cart import Cart
from orders.forms import CartAddProductForm, OrderCreateForm
from orders.models import OrderItem, Order
from products.models import Product


# Create your views here.
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        clean_data = form.cleaned_data
        cart.add(product=product, quantity=clean_data['quantity'], override_quantity=clean_data['override'])
    return redirect('orders:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        # Per ogni item nel carrello, aggiungi il form per aggiornare la quantità
        item['update_quantity_form'] = CartAddProductForm(initial={
                                            'quantity': item['quantity'],
                                            'override': True})
    return render(request, 'orders/cart_detail.html', {'cart': cart})

def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Collega l'ordine all'utente corrente se loggato
            if request.user.is_authenticated:
                order.user = request.user
            order.save() # Salva l'ordine con l'utente associato

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear() # Svuota il carrello dopo aver creato l'ordine
            return render(request, 'orders/order_created.html', {'order': order})
    else:
        # Se l'utente è loggato, pre-popola il form con i suoi dati
        if request.user.is_authenticated:
            user_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'address': request.user.address,
                'postal_code': request.user.cap,
                'city': request.user.city,
            }
            form = OrderCreateForm(user_data)
        else:
            form = OrderCreateForm()
    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/orders_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Ordine non trovato o non autorizzato.")
        return obj


@require_POST
@login_required
def order_pay_simulate(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.paid and order.status == 'pending':
        order.paid = True
        order.status = 'processing' # Dopo il pagamento, lo stato diventa "in elaborazione"
        order.save()
        messages.success(request, f"L'ordine #{order.id} è stato contrassegnato come pagato e in elaborazione!")
    else:
        messages.warning(request, f"L'ordine #{order.id} non può essere pagato in questo stato.")

    return redirect('orders:order_detail', order_id=order.id)


@require_POST
@login_required
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['pending', 'paid', 'processing']:
        order.status = 'cancelled'
        order.save()
        messages.info(request, f"L'ordine #{order.id} è stato annullato.")
    else:
        messages.error(request, f"L'ordine #{order.id} non può essere annullato in questo stato ({order.get_status_display()}).")

    return redirect('orders:order_detail', order_id=order.id)