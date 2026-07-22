from django.db import models
from django.core.exceptions import ValidationError

class SiteConfiguration(models.Model):
    # System settings
    comfyui_url = models.CharField(max_length=255, default='http://localhost:8188', help_text="ComfyUI server URL")
    under_maintenance = models.BooleanField(default=False, help_text="Enable maintenance mode for frontend")

    # Business entity details
    entity_name = models.CharField(max_length=255, default='MD AAQIF')
    registered_address = models.TextField(default='B-278/ GALI NO-4, JAITPUR PART-2, KHADDA COLONY, NEAR SONI MODERN PUBLIC SCHOOL, NEW DELHI-110044')
    support_phone = models.CharField(max_length=50, default='+91 8506021247')
    support_email = models.CharField(max_length=255, default='support@wondertale.in')
    support_hours = models.CharField(max_length=255, default='Mon - Fri, 10:00 AM - 6:00 PM')

    # Pricing & tax details
    currency_symbol = models.CharField(max_length=10, default='₹')
    currency_code = models.CharField(max_length=10, default='INR')
    is_tax_included = models.BooleanField(default=True)
    tax_note = models.CharField(max_length=100, default='Inclusive of all taxes')

    softcover_image = models.ImageField(upload_to='config/pricing/', null=True, blank=True)
    hardcover_image = models.ImageField(upload_to='config/pricing/', null=True, blank=True)

    # Shipping & delivery timelines
    estimated_delivery_time = models.CharField(max_length=100, default='7-8 working days')
    shipping_regions = models.TextField(default='Deliveries available across all pin codes in India.')
    courier_partners = models.TextField(default='Delhivery, BlueDart, and Speed Post')
    dispatch_timeline = models.CharField(max_length=255, default='Dispatched within 24-48 hours after photo approval.')

    # Cancellation & refund policies
    cancellation_window_hours = models.IntegerField(default=2)

    # Announcement & Discount Banner settings
    announcement_text = models.CharField(max_length=255, default='✨ New Story Alert: "The Crystal Cave" is now available for personalization! ✨', blank=True, help_text="Top header announcement text")
    announcement_enabled = models.BooleanField(default=True, help_text="Enable top header announcement bar")
    discount_bar_text = models.CharField(max_length=255, default='⚡ Limited Time Offer: Save up to 33% OFF on all custom storybooks today!', blank=True, help_text="Promotional discount banner text")
    discount_bar_enabled = models.BooleanField(default=True, help_text="Enable promotional discount banner")

    # Social proof counters
    viewing_min = models.IntegerField(default=60, help_text="Minimum range for active page viewers counter")
    viewing_max = models.IntegerField(default=99, help_text="Maximum range for active page viewers counter")
    crafting_min = models.IntegerField(default=8, help_text="Minimum range for stories being crafted counter")
    crafting_max = models.IntegerField(default=50, help_text="Maximum range for stories being crafted counter")

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError('There can be only one SiteConfiguration instance.')
        return super(SiteConfiguration, self).save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
