from django.http import JsonResponse
from .models import Review

def get_reviews_view(request):
    """
    API: Retrieve a list of active reviews.
    """
    reviews = Review.objects.filter(is_active=True).order_by('id')
    data = []
    for r in reviews:
        data.append({
            'id': r.id,
            'name': r.name,
            'location': r.location,
            'quote': r.quote,
            'rating': r.rating,
            'product_id': r.product.id if r.product else None,
            'user_id': r.user.id if r.user else None,
        })
    return JsonResponse(data, safe=False)
