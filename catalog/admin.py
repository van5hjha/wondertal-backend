from django.contrib import admin
from .models import Product, BookTemplate, PageTemplate, BeforeAfterSlide, ProductPreviewImage

class PageTemplateInline(admin.TabularInline):
    model = PageTemplate
    extra = 1
    fields = ('page_number', 'story_text', 'image_name', 'mask_image_name', 'is_preview')
    ordering = ('page_number',)

class ProductPreviewImageInline(admin.TabularInline):
    model = ProductPreviewImage
    extra = 1
    fields = ('image', 'order')
    ordering = ('order',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_range', 'price_hardcover', 'price_softcover', 'rating', 'review_count', 'is_active')
    list_filter = ('is_active', 'age_range')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductPreviewImageInline]


@admin.register(BookTemplate)
class BookTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'age_group', 'is_active', 'created_at')
    list_filter = ('is_active', 'age_group')
    search_fields = ('title', 'description')
    inlines = [PageTemplateInline]

@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ('book_template', 'page_number', 'is_preview')
    list_filter = ('is_preview', 'book_template')
    ordering = ('book_template', 'page_number')

@admin.register(BeforeAfterSlide)
class BeforeAfterSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)

