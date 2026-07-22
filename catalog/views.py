from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import BeforeAfterSlide, Product
from .serializers import ProductSerializer

class ProductPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

def get_sliders_view(request):
    """
    API: Retrieve a list of active before-after and static slides.
    """
    slides = BeforeAfterSlide.objects.filter(is_active=True).order_by('order', 'id')
    data = []
    for s in slides:
        before_url = request.build_absolute_uri(s.before_image.url) if s.before_image else ''
        after_url = request.build_absolute_uri(s.after_image.url) if s.after_image else ''
        img_url = request.build_absolute_uri(s.image.url) if s.image else before_url

        data.append({
            'id': s.id,
            'title': s.title or '',
            'type': s.slide_type,
            'beforeImageUrl': before_url,
            'afterImageUrl': after_url,
            'imageUrl': img_url,
        })
    return JsonResponse(data, safe=False)

@api_view(['GET'])
def get_products_view(request):
    """
    API: Retrieve a list of active products with pagination (6 products per page).
    """
    products = Product.objects.filter(is_active=True).order_by('id')
    category = request.query_params.get('category')
    if category:
        products = products.filter(category=category)
        
    paginator = ProductPagination()
    page = paginator.paginate_queryset(products, request)
    if page is not None:
        serializer = ProductSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    serializer = ProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)
