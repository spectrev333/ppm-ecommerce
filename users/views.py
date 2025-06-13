from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from users.forms import UserRegisterForm


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

