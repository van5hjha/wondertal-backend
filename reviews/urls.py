from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('api/reviews/', views.get_reviews_view, name='get_reviews'),
]
