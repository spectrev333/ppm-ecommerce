from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('', views.cart_detail, name='cart_detail'),
    path('create/', views.order_create, name='order_create'),
]