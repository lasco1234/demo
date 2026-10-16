from django.urls import path
from . import views

urlpatterns = [
    path('sales-history/', views.sales_history, name='sales_history'),
    path('sales-history/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('sales-return/', views.sales_return_list, name='sales_return_list'),
    path('sales-return/add/', views.sales_return_create, name='sales_return_create'),
    path('sales-return/<int:pk>/', views.sales_return_detail, name='sales_return_detail'),
    path('sale-item/<int:item_id>/update-qty/', views.update_sale_item_quantity, name='update_sale_item_qty'),
    path('sale-item/<int:item_id>/delete/', views.delete_sale_item, name='delete_sale_item'),
]