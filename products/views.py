from pyexpat.errors import messages

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from orders.forms import CartAddProductForm
from products.models import Product, Category


# Create your views here.
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    category = None

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            self.category = get_object_or_404(Category, slug = category_slug)
            return Product.objects.filter(category=self.category)
        return Product.objects.filter()

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected_category"] = self.category
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset = ...):
        return get_object_or_404(
            Product,
            id=self.kwargs["id"],
            slug=self.kwargs["slug"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart_product_form'] = CartAddProductForm()
        return context

def is_superuser_or_manager(user):
    return user.is_superuser or user.is_manager

class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verifica che l'utente sia un mangoero o un superuser."""
    def test_func(self):
        return is_superuser_or_manager(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Non sei autorizzato a accedere a questa pagina.")
        return redirect('products:product_list')


class ProductCreateView(ManagerRequiredMixin, CreateView):
    """Vista del manager per la creazione di un nuovo prodotto."""
    model = Product
    fields = ['category', 'name', 'image', 'description', 'price', 'available']
    template_name = 'products/manager/product_form.html'
    success_url = reverse_lazy('products:manager_product_list') # Reindirizza alla lista prodotti dopo creazione

    def form_valid(self, form):
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.name)
        return super().form_valid(form)


class ProductUpdateView(ManagerRequiredMixin, UpdateView):
    """Vista del manager per l'aggiornamento di un prodotto."""
    model = Product
    fields = ['category', 'name', 'slug', 'image', 'description', 'price', 'available']
    template_name = 'products/manager/product_form.html'
    success_url = reverse_lazy('products:manager_product_list')  # Reindirizza alla lista prodotti dopo creazione


class ProductDeleteView(ManagerRequiredMixin, DeleteView):
    """Vista del manager per la cancellazione di un prodotto."""
    model = Product
    template_name = 'products/manager/product_confirm_delete.html'
    success_url = reverse_lazy('products:manager_product_list')


class CategoryCreateView(ManagerRequiredMixin, CreateView):
    """Vista del manager per la creazione di una nuova categoria."""
    model = Category
    fields = ['name', 'slug']
    template_name = 'products/manager/category_form.html'
    success_url = reverse_lazy('products:manager_category_list') # O una lista di categorie

class CategoryUpdateView(ManagerRequiredMixin, UpdateView):
    """Vista del manager per l'aggiornamento di una categoria."""
    model = Category
    fields = ['name', 'slug']
    template_name = 'products/manager/category_form.html'
    success_url = reverse_lazy('products:manager_category_list')

class CategoryDeleteView(ManagerRequiredMixin, DeleteView):
    """Vista del manager per la cancellazione di una categoria."""
    model = Category
    template_name = 'products/manager/category_confirm_delete.html'
    success_url = reverse_lazy('products:manager_category_list')

class ManagerProductListView(ManagerRequiredMixin, ListView):
    """Vista del manager per la visualizzazione di tutti i prodotti."""
    model = Product
    template_name = 'products/manager/product_list_manager.html' # Nuovo template
    context_object_name = 'products'
    paginate_by = 10 # Se hai molti prodotti

class ManagerCategoryListView(ManagerRequiredMixin, ListView):
    """Vista del manager per la visualizzazione di tutte le categorie."""
    model = Category
    template_name = 'products/manager/category_list_manager.html' # Nuovo template
    context_object_name = 'categories'
    paginate_by = 10 # Se hai molte categorie
