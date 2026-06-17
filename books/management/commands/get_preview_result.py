import os
from django.core.management.base import BaseCommand, CommandError
from books.models import PreviewRequest
from books.processing import process_preview_request

class Command(BaseCommand):
    help = 'Fetches, processes (if pending/failed or forced), and prints the results of a PreviewRequest by its ID.'

    def add_arguments(self, parser):
        parser.add_argument('preview_id', type=str, help='The UUID of the PreviewRequest')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-processing of the PreviewRequest even if it is already completed.',
        )

    def handle(self, *args, **options):
        preview_id = options['preview_id']
        force = options['force']

        try:
            preview_req = PreviewRequest.objects.get(id=preview_id)
        except PreviewRequest.DoesNotExist:
            raise CommandError(f"PreviewRequest with ID '{preview_id}' not found.")
        except Exception as e:
            raise CommandError(f"Invalid UUID/ID format or database error: {e}")

        self.stdout.write(f"Found PreviewRequest {preview_req.id}:")
        self.stdout.write(f"  Template: {preview_req.book_template.title}")
        self.stdout.write(f"  Child Name: {preview_req.child_name or 'N/A'}")
        self.stdout.write(f"  Status: {preview_req.status}")
        self.stdout.write(f"  Faces count: {preview_req.faces.count()}")

        # Process if pending, failed, or forced
        should_process = preview_req.status in ['pending', 'failed'] or force

        if should_process:
            if force:
                self.stdout.write("Force flag is set. Re-processing...")
            else:
                self.stdout.write(f"Status is '{preview_req.status}'. Processing now...")

            try:
                # Call the processing function
                process_preview_request(preview_req)
                # Refresh from DB
                preview_req.refresh_from_db()
                self.stdout.write(self.style.SUCCESS(f"Processing completed with status: {preview_req.status}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error occurred during processing: {e}"))
                # Refresh from DB to get the failed status
                preview_req.refresh_from_db()
        else:
            self.stdout.write("PreviewRequest is already completed. Skipping processing. (Use --force to re-run)")

        # Fetch and display results
        results = preview_req.results.all().order_by('page_number')
        self.stdout.write(f"\nResults count: {results.count()}")
        for result in results:
            img_path = result.generated_image.path if result.generated_image else "No image file generated"
            self.stdout.write(f"  Page {result.page_number}: {img_path}")
