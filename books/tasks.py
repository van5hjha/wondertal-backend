import logging
from celery import shared_task
from books.models import BookRequest, PreviewRequest
from books.processing import process_book_request, process_preview_request

logger = logging.getLogger(__name__)

@shared_task
def process_preview_request_task(preview_request_id, page_number=None):
    logger.info(f"Celery task started: process_preview_request_task for request {preview_request_id}, page_number {page_number}")
    try:
        preview_request = PreviewRequest.objects.get(id=preview_request_id)
        process_preview_request(preview_request, page_number=page_number)
        logger.info(f"Celery task completed: process_preview_request_task for request {preview_request_id}, page_number {page_number}")
    except PreviewRequest.DoesNotExist:
        logger.error(f"PreviewRequest {preview_request_id} not found.")
    except Exception as e:
        logger.error(f"Error in process_preview_request_task: {e}", exc_info=True)
        raise e

@shared_task
def process_book_request_task(book_request_id):
    logger.info(f"Celery task started: process_book_request_task for request {book_request_id}")
    try:
        book_request = BookRequest.objects.get(id=book_request_id)
        process_book_request(book_request)
        logger.info(f"Celery task completed: process_book_request_task for request {book_request_id}")
    except BookRequest.DoesNotExist:
        logger.error(f"BookRequest {book_request_id} not found.")
    except Exception as e:
        logger.error(f"Error in process_book_request_task: {e}", exc_info=True)
        raise e
