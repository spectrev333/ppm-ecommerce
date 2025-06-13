from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from users.forms import UserRegisterForm, UserProfileUpdateForm
from users.models import CustomUser


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assegna l'utente al gruppo 'Customers' per default
            customer_group, created = Group.objects.get_or_create(name='Customers')
            user.groups.add(customer_group)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account creato per {username}! Ora puoi effettuare il login.')
            return redirect('login') # Reindirizza alla pagina di login
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Il tuo profilo è stato aggiornato con successo!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,"Si è verificato un errore durante l'aggiornamento del profilo. Controlla i campi.")
        return super().form_invalid(form)