from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'rating', 'is_active', 'created_at')
    list_filter = ('rating', 'is_active', 'created_at', 'product')
    search_fields = ('name', 'location', 'quote')
