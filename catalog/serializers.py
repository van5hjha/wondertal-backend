from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    bookTemplateId = serializers.SerializerMethodField()
    previewImages = serializers.SerializerMethodField()
    id = serializers.CharField(source='slug')
    ageRange = serializers.CharField(source='age_range')
    reviewCount = serializers.IntegerField(source='review_count')
    priceHardcover = serializers.IntegerField(source='price_hardcover')
    priceSoftcover = serializers.IntegerField(source='price_softcover')
    rating = serializers.FloatField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'ageRange', 'description', 'rating',
            'reviewCount', 'priceHardcover', 'priceSoftcover',
            'previewImages', 'features', 'bookTemplateId'
        ]

    def get_bookTemplateId(self, obj):
        bt = obj.booktemplate_set.filter(is_active=True).first()
        return bt.id if bt else None

    def get_previewImages(self, obj):
        request = self.context.get('request')
        urls = []
        for img in obj.preview_images.all().order_by('order', 'id'):
            if img.image:
                if request is not None:
                    urls.append(request.build_absolute_uri(img.image.url))
                else:
                    urls.append(img.image.url)
        return urls
