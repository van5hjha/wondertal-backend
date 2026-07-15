from rest_framework import serializers
from .models import SiteConfiguration

class SiteConfigurationSerializer(serializers.ModelSerializer):
    softcoverImageUrl = serializers.SerializerMethodField()
    hardcoverImageUrl = serializers.SerializerMethodField()

    class Meta:
        model = SiteConfiguration
        fields = '__all__'

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
