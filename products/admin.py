from django.contrib import admin

from products.models import Category, Product


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} # Rende lo slug automatico dal nome

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'category']
    list_editable = ['price', 'available'] # Permette di modificare direttamente dal listato
    prepopulated_fields = {'slug': ('name',)}