from django.urls import path
from . import views # Assicurati che views sia importato
from .views import UserProfileView # Importa UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'), # Nuovo URL per il profilo
]