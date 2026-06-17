from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('api/previews/', views.create_preview_view, name='create_preview'),
    path('api/previews/<uuid:preview_request_id>/start/', views.start_preview_view, name='start_preview'),
    path('api/previews/<uuid:preview_request_id>/status/', views.get_preview_status_view, name='get_preview_status'),
    path('api/previews/<uuid:preview_request_id>/regenerate/<int:page_number>/', views.regenerate_preview_page_view, name='regenerate_preview_page'),
]
