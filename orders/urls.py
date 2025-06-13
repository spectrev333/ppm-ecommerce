from django.urls import path
from . import views
from .views import OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('add/<int:product_id>/', views.cart_add, name='cart_add'), # Aggiungi prodotto al carrello
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'), # Rimuovi prodotto dal carrello
    path('', views.cart_detail, name='cart_detail'), # Carrello
    path('create/', views.order_create, name='order_create'), # Invia ordine
    path('list/', views.OrderListView.as_view(), name='orders_list'), # Ordini cliente
    path('<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),  # Dettaglio singolo ordine
    path('<int:order_id>/pay/', views.order_pay_simulate, name='order_pay_simulate'),  # Azione paga
    path('<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),  # Azione annulla
]