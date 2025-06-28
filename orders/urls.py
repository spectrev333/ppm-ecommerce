from django.urls import path
from . import views
from .views import OrderDetailView, ManagerOrderListView, ManagerOrderDetailView

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

    # URL Gestione Ordini per Manager
    path('manager/orders/', ManagerOrderListView.as_view(), name='manager_order_list'),
    path('manager/orders/<int:order_id>/', ManagerOrderDetailView.as_view(), name='manager_order_detail'),
    path('manager/orders/<int:order_id>/update_status/', views.manager_order_update_status,
         name='manager_order_update_status'),
    path('manager/orders/<int:order_id>/toggle_paid/', views.manager_order_toggle_paid,
         name='manager_order_toggle_paid'),
]