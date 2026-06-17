from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from books.models import BookRequest, PreviewRequest
from books.tasks import process_book_request_task, process_preview_request_task

@receiver(post_save, sender=PreviewRequest)
def trigger_preview_processing(sender, instance, created, **kwargs):
    if instance.status == 'pending':
        # Use on_commit to ensure the DB transaction is complete
        # before the Celery worker tries to fetch the request.
        transaction.on_commit(lambda: process_preview_request_task.delay(str(instance.id)))

@receiver(post_save, sender=BookRequest)
def trigger_book_processing(sender, instance, created, **kwargs):
    if instance.status == 'pending':
        transaction.on_commit(lambda: process_book_request_task.delay(instance.id))
