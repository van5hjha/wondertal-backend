import uuid
from django.db import models
from django.conf import settings
from catalog.models import BookTemplate, PageTemplate

class BookResult(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    book_template = models.ForeignKey(BookTemplate, on_delete=models.PROTECT)
    child_name = models.CharField(max_length=100)
    child_age = models.PositiveIntegerField(null=True, blank=True)
    child_gender = models.CharField(
        max_length=20, 
        choices=[('boy', 'Boy'), ('girl', 'Girl'), ('neutral', 'Neutral')]
    )
    child_hair_color = models.CharField(max_length=50, blank=True, null=True)
    child_skin_tone = models.CharField(max_length=50, blank=True, null=True)
    child_secondary_attributes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child_name}'s {self.book_template.title} ({self.id})"

class BookRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    book_template = models.ForeignKey(BookTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    contact_email = models.EmailField()
    child_name = models.CharField(max_length=100)
    child_age = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, 
        default='pending', 
        choices=[('pending', 'Pending'), ('generating', 'Generating'), ('created', 'Created'), ('failed', 'Failed')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request for {self.child_name} ({self.status})"

class PreviewRequest(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    book_template = models.ForeignKey(BookTemplate, on_delete=models.PROTECT)
    contact_email = models.EmailField(blank=True, null=True)
    child_name = models.CharField(max_length=100, blank=True, null=True)
    child_age = models.PositiveIntegerField(blank=True, null=True)
    child_gender = models.CharField(
        max_length=20, 
        choices=[('boy', 'Boy'), ('girl', 'Girl'), ('neutral', 'Neutral')],
        default='neutral'
    )
    status = models.CharField(
        max_length=20, 
        default='pending', 
        choices=[('pending', 'Pending'), ('generating', 'Generating'), ('completed', 'Completed'), ('failed', 'Failed')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preview Request for {self.child_name or self.book_template.title} ({self.status})"

class PreviewResult(models.Model):
    preview_request = models.ForeignKey(PreviewRequest, on_delete=models.CASCADE, related_name='results')
    page_template = models.ForeignKey(PageTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    page_number = models.PositiveIntegerField()
    generated_image = models.ImageField(upload_to='previews/pages/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ('preview_request', 'page_number')

    def __str__(self):
        return f"Preview Result - Page {self.page_number} ({self.preview_request.id})"

class ChildFace(models.Model):
    book_result = models.ForeignKey(
        BookResult, 
        on_delete=models.CASCADE, 
        related_name='faces', 
        null=True, 
        blank=True
    )
    book_request = models.ForeignKey(
        BookRequest, 
        on_delete=models.CASCADE, 
        related_name='faces', 
        null=True, 
        blank=True
    )
    preview_request = models.ForeignKey(
        PreviewRequest,
        on_delete=models.CASCADE,
        related_name='faces',
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='child_faces/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.book_result:
            return f"Face for BookResult {self.book_result.id}"
        elif self.book_request:
            return f"Face for BookRequest {self.book_request.id}"
        elif self.preview_request:
            return f"Face for PreviewRequest {self.preview_request.id}"
        return f"Orphaned Face {self.id}"

class BookPage(models.Model):
    book_result = models.ForeignKey(BookResult, on_delete=models.CASCADE, related_name='pages')
    page_template = models.ForeignKey(PageTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    page_number = models.PositiveIntegerField()
    generated_image = models.ImageField(upload_to='generated_books/pages/', null=True, blank=True)
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ('book_result', 'page_number')

    def __str__(self):
        return f"{self.book_result.child_name}'s Book - Page {self.page_number}"
