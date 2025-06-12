from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from products.models import Product, Category


# Create your views here.
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            category = get_object_or_404(Category, slug = category_slug)
            return Product.objects.filter(category=category, available=True)
        return Product.objects.filter(available=True)

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset = ...):
        return get_object_or_404(
            Product,
            id=self.kwargs["id"],
            slug=self.kwargs["slug"],
            available=True
        )