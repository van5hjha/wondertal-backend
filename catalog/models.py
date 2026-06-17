from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New fields to match frontend expectations
    age_range = models.CharField(max_length=50, default="3-8 yrs")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    review_count = models.PositiveIntegerField(default=0)
    price_hardcover = models.PositiveIntegerField(default=1499)
    price_softcover = models.PositiveIntegerField(default=999)
    features = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title

class ProductPreviewImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='preview_images')
    image = models.ImageField(upload_to='catalog/previews/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Preview Image for {self.product.title} - {self.image.name if self.image else 'No Image'}"


class BookTemplate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='templates/covers/', null=True, blank=True)
    age_group = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PageTemplate(models.Model):
    book_template = models.ForeignKey(BookTemplate, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveIntegerField()
    story_text = models.TextField(blank=True, null=True)
    image_name = models.CharField(max_length=255, null=True, blank=True)
    mask_image_name = models.CharField(max_length=255, null=True, blank=True)
    is_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ['page_number']
        unique_together = ('book_template', 'page_number')

    def __str__(self):
        return f"{self.book_template.title} - Page {self.page_number}"

class BeforeAfterSlide(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    before_image = models.ImageField(upload_to='sliders/')
    after_image = models.ImageField(upload_to='sliders/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"Slide {self.id}"
