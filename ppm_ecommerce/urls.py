"""
URL configuration for ppm_ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

import users.views
from ppm_ecommerce import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('orders/', include('orders.urls')),

    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', next_page='products:product_list'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='products:product_list'), name='logout'),
    path('users/', include('users.urls')),
    path('', include('products.urls')),
]

if settings.DEBUG: # In non debug vengono serviti dal webserver
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

