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
