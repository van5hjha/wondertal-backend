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

class ProductPreviewItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='preview_items')
    item_type = models.CharField(max_length=20, choices=[('static', 'Static'), ('slide', 'Slide')], default='static')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.item_type.capitalize()} Preview Item for {self.product.title}"

class ProductPreviewImage(models.Model):
    item = models.ForeignKey(ProductPreviewItem, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='catalog/previews/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.item}"


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
    image = models.ImageField(upload_to='templates/pages/images/', null=True, blank=True)
    mask_image = models.ImageField(upload_to='templates/pages/masks/', null=True, blank=True)
    svg_template = models.FileField(upload_to='templates/svgs/', default='templates/svgs/default.svg')
    is_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ['page_number']
        unique_together = ('book_template', 'page_number')

    def __str__(self):
        return f"{self.book_template.title} - Page {self.page_number}"

class BeforeAfterSlide(models.Model):
    SLIDE_TYPE_CHOICES = [
        ('before_after', 'Before-After'),
        ('static', 'Static'),
    ]

    title = models.CharField(max_length=100, blank=True, null=True)
    slide_type = models.CharField(max_length=20, choices=SLIDE_TYPE_CHOICES, default='before_after')
    before_image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    after_image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    image = models.ImageField(upload_to='sliders/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"Slide {self.id}"
