from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from orders.cart import Cart
from orders.forms import CartAddProductForm, OrderCreateForm
from orders.models import OrderItem, Order
from products.models import Product
from products.views import ManagerRequiredMixin, is_superuser_or_manager


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
    if not request.user.is_authenticated:
        messages.warning(request, "Per effettuare un ordine, devi essere loggato.")
        return redirect(f"{reverse('login')}?next={request.path}")

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            unavailable_products = []
            for item in cart:
                product = Product.objects.filter(id=item['product'].id, available=True).first()
                if not product:
                    unavailable_products.append(str(item['product']))
            if unavailable_products:
                messages.error(
                    request,
                    f'I prodotti seguenti non sono disponibili: {', '.join(unavailable_products)}'
                )
                return redirect('orders:cart_detail')

            order = form.save(commit=False)
            order.user = request.user # Collega utente
            order.save()

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear() # Svuota il carrello dopo aver creato l'ordine
            return render(request, 'orders/order_created.html', {'order': order})
    else:
        # Pre-compila i campi già noti
        user_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'address': request.user.address,
            'postal_code': request.user.cap,
            'city': request.user.city,
        }
        form = OrderCreateForm(user_data)
    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/user_orders.html'
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


class ManagerOrderListView(ManagerRequiredMixin, ListView):
    model = Order
    template_name = 'orders/manager/order_list_manager.html' # Nuovo template
    context_object_name = 'orders'
    paginate_by = 20 # Potrebbe esserci un numero maggiore di ordini

    def get_queryset(self):
        # I manager possono vedere tutti gli ordini
        return Order.objects.all().order_by('-created')


class ManagerOrderDetailView(ManagerRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/manager/order_detail_manager.html' # Nuovo template
    context_object_name = 'order'
    pk_url_kwarg = 'order_id' # Il nome del parametro URL per l'ID dell'ordine

    def get_object(self, queryset=None):
        # Il manager può vedere qualsiasi ordine per ID
        return get_object_or_404(Order, id=self.kwargs['order_id'])


@require_POST
@user_passes_test(is_superuser_or_manager, login_url=reverse_lazy('login'), redirect_field_name=None)
def manager_order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status') # Il nuovo stato viene passato via POST

    if new_status and new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
        order.status = new_status
        # Logica aggiuntiva se il manager imposta a 'paid', potresti aggiornare anche order.paid
        if new_status == 'paid':
            order.paid = True
        # Se lo stato cambia da 'paid' a 'pending' o 'cancelled', paid dovrebbe tornare a False
        if new_status in ['pending', 'cancelled']:
            order.paid = False

        order.save()
        messages.success(request, f"Stato dell'ordine #{order.id} aggiornato a '{order.get_status_display()}' con successo.")
    else:
        messages.error(request, "Stato non valido o non fornito.")

    return redirect('orders:manager_order_detail', order_id=order.id)


@require_POST
@user_passes_test(is_superuser_or_manager, login_url=reverse_lazy('login'), redirect_field_name=None)
def manager_order_toggle_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.paid = not order.paid
    # Se il manager imposta a pagato, imposta lo stato su 'processing' se era 'pending'
    if order.paid and order.status == 'pending':
        order.status = 'processing'
    # Se il manager imposta a non pagato, imposta lo stato su 'pending' se era 'paid' o 'processing'
    elif not order.paid and order.status in ['paid', 'processing', 'shipped', 'completed']: # Se spagato un ordine già processato/spedito
        order.status = 'pending' # O potresti volere uno stato tipo 'refunded'

    order.save()
    status_msg = "pagato" if order.paid else "non pagato"
    messages.success(request, f"Stato pagamento ordine #{order.id} aggiornato a '{status_msg}' e stato ordine a '{order.get_status_display()}'.")
    return redirect('orders:manager_order_detail', order_id=order.id)