from django.contrib import admin
from .models import BookResult, BookRequest, ChildFace, BookPage, PreviewRequest, PreviewResult

class ChildFaceInline(admin.TabularInline):
    model = ChildFace
    extra = 1
    fields = ('image',)

class BookPageInline(admin.TabularInline):
    model = BookPage
    extra = 1
    fields = ('page_number', 'generated_image', 'is_preview')
    ordering = ('page_number',)

class PreviewResultInline(admin.TabularInline):
    model = PreviewResult
    extra = 1
    fields = ('page_number', 'generated_image')
    ordering = ('page_number',)

@admin.register(BookResult)
class BookResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'child_name', 'child_age', 'child_gender', 'book_template', 'created_at')
    list_filter = ('child_gender', 'book_template')
    search_fields = ('child_name', 'id')
    inlines = [ChildFaceInline, BookPageInline]

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'child_age', 'contact_email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('child_name', 'contact_email')
    inlines = [ChildFaceInline]

@admin.register(PreviewRequest)
class PreviewRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_template', 'contact_email', 'status', 'created_at')
    list_filter = ('status', 'book_template')
    search_fields = ('contact_email', 'child_name', 'id')
    inlines = [ChildFaceInline, PreviewResultInline]

@admin.register(PreviewResult)
class PreviewResultAdmin(admin.ModelAdmin):
    list_display = ('preview_request', 'page_number', 'created_at')
    list_filter = ('preview_request__book_template',)
    ordering = ('preview_request', 'page_number')

@admin.register(ChildFace)
class ChildFaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_result', 'book_request', 'preview_request', 'created_at')
    list_filter = ('created_at',)

@admin.register(BookPage)
class BookPageAdmin(admin.ModelAdmin):
    list_display = ('book_result', 'page_number', 'is_preview')
    list_filter = ('is_preview', 'book_result__book_template')
    ordering = ('book_result', 'page_number')
