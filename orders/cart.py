# orders/cart.py
from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Inizializza il carrello.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # salva un carrello vuoto nella sessione
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Aggiunge un prodotto al carrello o ne aggiorna la quantità.
        Override serve nella vista di dettaglio del carrello, è un campo nascosto che viene automaticamente
        settato dalla view.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # marca la sessione come "modificata" per assicurarsi che venga salvata
        self.session.modified = True

    def remove(self, product):
        """
        Rimuove un prodotto dal carrello.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Itera sugli articoli del carrello e recupera i prodotti dal database.
        """
        product_ids = self.cart.keys()
        # recupera gli oggetti prodotto e aggiungili al carrello
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Restituisce il numero totale di articoli nel carrello.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Restituisce il costo totale degli articoli nel carrello.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Rimuove il carrello dalla sessione.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()