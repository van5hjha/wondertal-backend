from django.contrib import admin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.count() > 0:
            return False
        return super().has_add_permission(request)

    fieldsets = (
        ('System Settings', {
            'fields': ('comfyui_url', 'under_maintenance')
        }),
        ('Business Entity Details', {
            'fields': ('entity_name', 'registered_address', 'support_phone', 'support_email', 'support_hours')
        }),
        ('Pricing & Tax Details', {
            'fields': ('currency_symbol', 'currency_code', 'is_tax_included', 'tax_note', 'softcover_image', 'hardcover_image')
        }),
        ('Shipping & Delivery Timelines', {
            'fields': ('estimated_delivery_time', 'shipping_regions', 'courier_partners', 'dispatch_timeline')
        }),
        ('Cancellation & Refund Policies', {
            'fields': ('cancellation_window_hours',)
        }),
        ('Announcement & Discount Banners', {
            'fields': ('announcement_enabled', 'announcement_text', 'discount_bar_enabled', 'discount_bar_text')
        }),
        ('Social Proof & Live Stats', {
            'fields': ('viewing_min', 'viewing_max', 'crafting_min', 'crafting_max')
        }),
    )
