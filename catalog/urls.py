from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('api/sliders/', views.get_sliders_view, name='get_sliders'),
    path('api/products/', views.get_products_view, name='get_products'),
]

