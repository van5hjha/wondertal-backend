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

        import re
        try:
            def split_paint_order_stroke(match):
                attrs = match.group(1)
                inner_content = match.group(2)
                style_match = re.search(r'style="([^"]*)"', attrs)
                if not style_match:
                    return match.group(0)
                style_content = style_match.group(1)
                
                # Find the stroke color to use as the fill color for the bottom stroke layer
                # to ensure the layout engine uses identical text metrics/baseline alignment
                stroke_color_match = re.search(r'stroke:\s*([^;]+);?', style_content)
                stroke_color = stroke_color_match.group(1).strip() if stroke_color_match else 'none'
                
                if stroke_color != 'none':
                    stroke_style = re.sub(r'fill:\s*[^;]+;?', f'fill: {stroke_color};', style_content)
                else:
                    stroke_style = re.sub(r'fill:\s*[^;]+;?', 'fill: none;', style_content)
                    
                fill_style = re.sub(r'stroke:\s*[^;]+;?', 'stroke: none;', style_content)
                
                stroke_attrs = attrs.replace(f'style="{style_content}"', f'style="{stroke_style}"')
                fill_attrs = attrs.replace(f'style="{style_content}"', f'style="{fill_style}"')
                return f'<text {stroke_attrs}>{inner_content}</text>\n<text {fill_attrs}>{inner_content}</text>'

            for svg_path in svg_paths:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                normalized_content = re.sub(r'rgb\(\s*([\d\.]+)%\s+([\d\.]+)%\s+([\d\.]+)%\s*\)', r'rgb(\1%, \2%, \3%)', content)
                
                # Parse outline filters and emulate them as standard strokes
                filters = {}
                filter_pattern = re.compile(r'<filter\s+[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</filter>', re.DOTALL)
                for m in filter_pattern.finditer(normalized_content):
                    filter_id = m.group(1)
                    filter_body = m.group(2)
                    radius_match = re.search(r'<feMorphology\s+[^>]*radius=["\']([^"\']+)["\']', filter_body)
                    radius = float(radius_match.group(1)) if radius_match else 10.0
                    color_match = re.search(r'<feFlood\s+[^>]*flood-color=["\']([^"\']+)["\']', filter_body)
                    color = color_match.group(1) if color_match else '#ff0000'
                    filters[filter_id] = {'radius': radius, 'color': color}

                def process_text_filters(match):
                    attrs = match.group(1)
                    inner_content = match.group(2)
                    style_match = re.search(r'style=["\']([^"\']*)["\']', attrs)
                    if not style_match:
                        return match.group(0)
                    style_content = style_match.group(1)
                    filter_url_match = re.search(r'filter:\s*url\((?:&quot;)?#([^&\)]+)(?:&quot;)?\);?', style_content)
                    if not filter_url_match:
                        return match.group(0)
                    filter_id = filter_url_match.group(1)
                    if filter_id in filters:
                        f_info = filters[filter_id]
                        new_style = style_content
                        new_style = re.sub(r'filter:\s*url\([^\)]+\);?', '', new_style)
                        new_style = re.sub(r'stroke-width:\s*[^;]+;?', '', new_style)
                        new_style = re.sub(r'paint-order:\s*[^;]+;?', '', new_style)
                        new_style = re.sub(r'stroke:\s*[^;]+;?', '', new_style)
                        new_style = re.sub(r'stroke-linejoin:\s*[^;]+;?', '', new_style)
                        new_style = re.sub(r'stroke-miterlimit:\s*[^;]+;?', '', new_style)
                        stroke_width = f_info['radius'] * 2
                        stroke_color = f_info['color']
                        if new_style and not new_style.strip().endswith(';'):
                            new_style += ';'
                        new_style += f' stroke: {stroke_color}; stroke-width: {stroke_width}px; paint-order: stroke; stroke-linejoin: miter; stroke-miterlimit: 10;'
                        attrs_replaced = attrs.replace(style_match.group(0), f'style="{new_style}"')
                        return f'<text {attrs_replaced}>{inner_content}</text>'
                    return match.group(0)

                normalized_content = re.sub(
                    r'<text\s+([^>]*style=["\'][^"\']*filter:\s*url[^"\']*["\'][^>]*)>(.*?)</text>',
                    process_text_filters,
                    normalized_content,
                    flags=re.DOTALL
                )

                normalized_content = re.sub(r'<text\s+([^>]*style="[^"]*paint-order:\s*stroke;[^"]*"[^>]*)>(.*?)</text>', split_paint_order_stroke, normalized_content, flags=re.DOTALL)
                pdf_bytes = cairosvg.svg2pdf(bytestring=normalized_content.encode('utf-8'))
                merger.append(BytesIO(pdf_bytes))
            
            with open(final_pdf_path, 'wb') as f:
                merger.write(f)
                
            self.stdout.write(self.style.SUCCESS(f"Successfully generated PDF at: {final_pdf_path}"))
        except Exception as e:
            raise CommandError(f"Error generating PDF: {str(e)}")
