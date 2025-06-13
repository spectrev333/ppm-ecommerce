from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from orders.cart import Cart
from orders.forms import CartAddProductForm, OrderCreateForm
from orders.models import OrderItem
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
                'phone_number': request.user.phone_number,
            }
            form = OrderCreateForm(initial=user_data)
        else:
            form = OrderCreateForm()
    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})

