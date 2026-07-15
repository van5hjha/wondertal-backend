import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from catalog.models import BookTemplate
from .models import PreviewRequest, ChildFace
from .tasks import process_preview_request_task

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def create_preview_view(request):
    """
    API 1: Create a Preview Request
    Accepts multipart/form-data:
      - book_template_id (int, required)
      - child_name (str, required)
      - child_age (int, required)
      - child_gender (str, required: boy, girl, neutral)
      - photos (exactly 3 files uploaded, or keys photo1, photo2, photo3)
    """
    # 1. Extract POST parameters
    book_template_id = request.POST.get('book_template_id')
    contact_email = request.POST.get('contact_email')
    child_name = request.POST.get('child_name')
    child_age_str = request.POST.get('child_age')
    child_gender = request.POST.get('child_gender')

    # 2. Basic parameter validation
    errors = {}
    if not book_template_id:
        errors['book_template_id'] = 'This field is required.'
    if not contact_email:
        errors['contact_email'] = 'This field is required.'
    if not child_name:
        errors['child_name'] = 'This field is required.'
    if not child_age_str:
        errors['child_age'] = 'This field is required.'
    if not child_gender:
        errors['child_gender'] = 'This field is required.'
    elif child_gender not in ['boy', 'girl', 'neutral']:
        errors['child_gender'] = "Must be one of: 'boy', 'girl', 'neutral'."

    if errors:
        return JsonResponse({'error': 'Validation failed', 'details': errors}, status=400)

    # Validate book_template exists
    try:
        book_template = BookTemplate.objects.get(id=book_template_id)
    except (ValueError, BookTemplate.DoesNotExist):
        return JsonResponse({'error': f'BookTemplate with id {book_template_id} does not exist.'}, status=400)

    # Validate child_age is integer
    try:
        child_age = int(child_age_str)
        if child_age < 0:
            raise ValueError()
    except ValueError:
        return JsonResponse({'error': 'child_age must be a positive integer.'}, status=400)

    # 3. Extract and validate uploaded photos
    uploaded_files = []
    # Try specific named fields
    for key in ['photo1', 'photo2', 'photo3']:
        if key in request.FILES:
            uploaded_files.append(request.FILES[key])
            
    # Try list of files named 'photos' if specific named fields are not fully used
    if not uploaded_files:
        uploaded_files = request.FILES.getlist('photos')
        
    # If still empty/partial, grab any uploaded files in request.FILES
    if not uploaded_files:
        uploaded_files = list(request.FILES.values())

    if len(uploaded_files) != 3:
        return JsonResponse({
            'error': f'Exactly 3 photos are required. Received {len(uploaded_files)}.'
        }, status=400)

    # 4. Create PreviewRequest and ChildFaces
    preview_request = PreviewRequest.objects.create(
        book_template=book_template,
        contact_email=contact_email,
        child_name=child_name,
        child_age=child_age,
        child_gender=child_gender,
        status='pending'
    )

    for photo in uploaded_files:
        ChildFace.objects.create(
            preview_request=preview_request,
            image=photo
        )

    return JsonResponse({
        'preview_request_id': str(preview_request.id),
        'status': preview_request.status,
        'message': 'Preview session created successfully. Ready to generate.'
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def start_preview_view(request, preview_request_id):
    """
    API 2: Start generating the preview
    """
    try:
        preview_request = PreviewRequest.objects.get(id=preview_request_id)
    except (ValueError, PreviewRequest.DoesNotExist):
        return JsonResponse({'error': f'PreviewRequest with id {preview_request_id} does not exist.'}, status=404)

    # Trigger background Celery task
    process_preview_request_task.delay(str(preview_request.id))

    return JsonResponse({
        'preview_request_id': str(preview_request.id),
        'status': preview_request.status,
        'message': 'Preview generation started.'
    }, status=200)


@require_http_methods(["GET"])
def get_preview_status_view(request, preview_request_id):
    """
    API 3: Check preview generation status and retrieve completed preview pages
    """
    try:
        preview_request = PreviewRequest.objects.get(id=preview_request_id)
    except (ValueError, PreviewRequest.DoesNotExist):
        return JsonResponse({'error': f'PreviewRequest with id {preview_request_id} does not exist.'}, status=404)

    # Gather results if status is completed (or any generated pages)
    pages = []
    if preview_request.status == 'completed':
        results = preview_request.results.all().order_by('page_number')
        for res in results:
            image_url = request.build_absolute_uri(res.generated_svg.url) if res.generated_svg else request.build_absolute_uri(res.raw_image.url) if res.raw_image else None
            pages.append({
                'page_number': res.page_number,
                'image_url': image_url
            })

    return JsonResponse({
        'preview_request_id': str(preview_request.id),
        'status': preview_request.status,
        'pages': pages
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def regenerate_preview_page_view(request, preview_request_id, page_number):
    """
    API 4: Regenerate a specific preview page result
    """
    try:
        preview_request = PreviewRequest.objects.get(id=preview_request_id)
    except (ValueError, PreviewRequest.DoesNotExist):
        return JsonResponse({'error': f'PreviewRequest with id {preview_request_id} does not exist.'}, status=404)

    # Validate that the requested page is indeed a preview page in this template
    has_preview_page = preview_request.book_template.pages.filter(
        page_number=page_number, 
        is_preview=True
    ).exists()
    
    if not has_preview_page:
        return JsonResponse({
            'error': f'Page number {page_number} is not a valid preview page for this template.'
        }, status=400)

    # Trigger background Celery task
    process_preview_request_task.delay(str(preview_request.id), page_number=page_number)

    return JsonResponse({
        'preview_request_id': str(preview_request.id),
        'page_number': page_number,
        'status': 'generating',
        'message': f'Regeneration of page {page_number} started.'
    }, status=200)
