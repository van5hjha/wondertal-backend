import time
from django.core.management.base import BaseCommand
from books.models import BookRequest, PreviewRequest
from books.processing import process_book_request, process_preview_request

class Command(BaseCommand):
    help = 'Processes pending BookRequest and PreviewRequest records by integrating with ComfyUI.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once to process current pending requests and exit.',
        )
        parser.add_argument(
            '--sleep',
            type=int,
            default=5,
            help='Number of seconds to sleep between checks when running in daemon mode.',
        )

    def handle(self, *args, **options):
        once = options['once']
        sleep_time = options['sleep']

        self.stdout.write("Starting request processing worker...")
        
        while True:
            # 1. Process Preview Requests
            pending_previews = PreviewRequest.objects.filter(status='pending').order_by('created_at')
            if pending_previews.exists():
                self.stdout.write(f"Found {pending_previews.count()} pending preview requests.")
                for req in pending_previews:
                    self.stdout.write(f"Processing PreviewRequest: {req.id}")
                    try:
                        process_preview_request(req)
                        self.stdout.write(self.style.SUCCESS(f"Successfully processed PreviewRequest {req.id}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Failed to process PreviewRequest {req.id}: {e}"))
                continue

            # 2. Process Book Requests
            pending_books = BookRequest.objects.filter(status='pending').order_by('created_at')
            if pending_books.exists():
                self.stdout.write(f"Found {pending_books.count()} pending book requests.")
                for req in pending_books:
                    self.stdout.write(f"Processing BookRequest: {req.id}")
                    try:
                        process_book_request(req)
                        self.stdout.write(self.style.SUCCESS(f"Successfully processed BookRequest {req.id}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Failed to process BookRequest {req.id}: {e}"))
                continue

            if once:
                self.stdout.write("No pending requests found. Exiting.")
                break

            time.sleep(sleep_time)
