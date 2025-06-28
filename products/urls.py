from django.urls import path
from .views import ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView, \
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView, ManagerProductListView, ManagerCategoryListView

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    # URL per la gestione dei prodotti (solo manager)
    path('manage/product/create/', ProductCreateView.as_view(), name='product_create'),
    path('manage/product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('manage/product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('manage/products/', ManagerProductListView.as_view(), name='manager_product_list'),

    # URL per la gestione delle categorie (solo manager)
    path('manage/category/create/', CategoryCreateView.as_view(), name='category_create'),
    path('manage/category/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('manage/category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('manage/categories/', ManagerCategoryListView.as_view(), name='manager_category_list'),

]