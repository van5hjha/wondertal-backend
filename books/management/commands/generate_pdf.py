import os
from io import BytesIO
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from books.models import PreviewRequest, BookRequest

try:
    import cairosvg
    from pypdf import PdfWriter, PdfReader
except ImportError:
    raise CommandError("Please install cairosvg and pypdf (e.g. pip install cairosvg pypdf)")

class Command(BaseCommand):
    help = 'Generates a combined PDF from the SVGs of a PreviewRequest or BookRequest'

    def add_arguments(self, parser):
        parser.add_argument('--preview', type=str, help='ID of the PreviewRequest')
        parser.add_argument('--book', type=str, help='ID of the BookRequest')

    def handle(self, *args, **options):
        preview_id = options.get('preview')
        book_id = options.get('book')

        if not preview_id and not book_id:
            raise CommandError("You must provide either --preview or --book")
        if preview_id and book_id:
            raise CommandError("Provide either --preview or --book, not both")

        svg_paths = []
        output_filename = ""

        if preview_id:
            try:
                pr = PreviewRequest.objects.get(id=preview_id)
            except PreviewRequest.DoesNotExist:
                raise CommandError(f"PreviewRequest {preview_id} does not exist.")
            
            # Get pages ordered by page number
            results = pr.results.all().order_by('page_number')
            for res in results:
                if res.generated_svg:
                    svg_paths.append(res.generated_svg.path)
            
            output_filename = f"preview_{preview_id}.pdf"
            
        elif book_id:
            try:
                br = BookRequest.objects.get(id=book_id)
            except BookRequest.DoesNotExist:
                raise CommandError(f"BookRequest {book_id} does not exist.")
            
            # Since BookRequest doesn't have direct results (it creates a BookResult)
            # Find the BookResult first
            if not getattr(br, 'book_result', None):
                # Try finding it through face or just assume there's one logic
                # For now, let's find the BookResult associated with this request
                faces = br.faces.all()
                if faces and faces[0].book_result:
                    book_result = faces[0].book_result
                else:
                    raise CommandError("Could not find generated BookResult for this BookRequest.")
            else:
                book_result = br.book_result
                
            pages = book_result.pages.all().order_by('page_number')
            for p in pages:
                if p.generated_svg:
                    svg_paths.append(p.generated_svg.path)
            
            output_filename = f"book_{book_id}.pdf"

        if not svg_paths:
            raise CommandError("No SVGs found for the given request.")

        self.stdout.write(f"Found {len(svg_paths)} SVG pages. Generating PDF...")

        output_path = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        os.makedirs(output_path, exist_ok=True)
        final_pdf_path = os.path.join(output_path, output_filename)

        merger = PdfWriter()

        try:
            for svg_path in svg_paths:
                pdf_bytes = cairosvg.svg2pdf(url=svg_path)
                merger.append(BytesIO(pdf_bytes))
            
            with open(final_pdf_path, 'wb') as f:
                merger.write(f)
                
            self.stdout.write(self.style.SUCCESS(f"Successfully generated PDF at: {final_pdf_path}"))
        except Exception as e:
            raise CommandError(f"Error generating PDF: {str(e)}")
