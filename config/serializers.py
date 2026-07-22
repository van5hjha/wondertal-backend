import random
from rest_framework import serializers
from .models import SiteConfiguration

class SiteConfigurationSerializer(serializers.ModelSerializer):
    softcoverImageUrl = serializers.SerializerMethodField()
    hardcoverImageUrl = serializers.SerializerMethodField()
    active_viewing_count = serializers.SerializerMethodField()
    active_crafting_count = serializers.SerializerMethodField()

    class Meta:
        model = SiteConfiguration
        fields = '__all__'

    def get_active_viewing_count(self, obj):
        v_min = min(obj.viewing_min, obj.viewing_max)
        v_max = max(obj.viewing_min, obj.viewing_max)
        return random.randint(v_min, v_max)

    def get_active_crafting_count(self, obj):
        c_min = min(obj.crafting_min, obj.crafting_max)
        c_max = max(obj.crafting_min, obj.crafting_max)
        return random.randint(c_min, c_max)

    def get_softcoverImageUrl(self, obj):
        request = self.context.get('request')
        if obj.softcover_image and request:
            return request.build_absolute_uri(obj.softcover_image.url)
        return None

    def get_hardcoverImageUrl(self, obj):
        request = self.context.get('request')
        if obj.hardcover_image and request:
            return request.build_absolute_uri(obj.hardcover_image.url)
        return None
