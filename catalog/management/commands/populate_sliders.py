import os
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
from catalog.models import BeforeAfterSlide

class Command(BaseCommand):
    help = "Populates BeforeAfterSlide records with local assets and remote downloads."

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing slides...")
        BeforeAfterSlide.objects.all().delete()

        # Define slide details
        slides_data = [
            {
                "title": "Space Explorer",
                "slide_type": "before_after",
                "order": 0,
                "type": "local",
                "before_filename": "before_image.png",
                "after_filename": "after_image.jpg",
            },
            {
                "title": "Magical Art Showcase",
                "slide_type": "static",
                "order": 1,
                "type": "local",
                "image_filename": "after_image.jpg",
            },
            {
                "title": "Safari Adventure",
                "slide_type": "before_after",
                "order": 2,
                "type": "remote",
                "before_url": "https://images.unsplash.com/photo-1503919545889-aef636e10ad4?auto=format&fit=crop&q=80&w=600",
                "after_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuC809sEA-5iptDaCin_DQRyUp2xRw_1BGTdAOAQrsj7xo_j2bGl-fUgCcnWUGRJRtCWcC3887NKb7kJFQCOKUXzK8krcp48t7UjbGsm0usL6T4oLMJSCorTz9oxokWkHKuNPoHU-54DrThkAa0ZeLVERzUSujSDfP2lOVS6Q6Odbr-POPRCelw1fyIcc1rlcgAqaWGBz6UMzwk1zbJR3BHTErT3I8en7vecnxQiTDp6zn2THM3DzSf0ympJ0TvgttHkbCxqdYRPDWg",
            },
            {
                "title": "Little Wizard",
                "slide_type": "before_after",
                "order": 3,
                "type": "remote",
                "before_url": "https://images.unsplash.com/photo-1519457431-44ccd64a579b?auto=format&fit=crop&q=80&w=600",
                "after_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBwtuNeje1NSPY0sdZBS7aJt5ktlibCJA0evDiOMNCJkhMoN-CP4v4EuQdIqHVUM7dzK9aWda0oXmoilbGz6s_IQ_qNPo1Bnlo5mHad2FQkfTbGjdbofQ7osSHo2IBn-pDStj0p1R5XwlWiZkDTHoUoG6gDhJyTXgJ-zFyA-jaJCifk5bi2ewfzHIfasdGn1wo794x_2Y-wR-brI7-G9gJSMBXaFj-CJpzSWvNNj0Jntkgvb28uM5m_S0ngi_T3nCfiKaw-U6Kxtkc",
            }
        ]

        frontend_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'frontend'))

        for data in slides_data:
            self.stdout.write(f"Creating slide: {data['title']} ({data['slide_type']})...")
            slide = BeforeAfterSlide.objects.create(
                title=data["title"],
                slide_type=data["slide_type"],
                order=data["order"]
            )

            if data["type"] == "local":
                if data["slide_type"] == "static":
                    img_path = os.path.join(frontend_dir, 'assets', 'images', data["image_filename"])
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            slide.image.save(data["image_filename"], File(f), save=True)
                else:
                    before_path = os.path.join(frontend_dir, 'assets', 'images', data["before_filename"])
                    after_path = os.path.join(frontend_dir, 'assets', 'images', data["after_filename"])

                    if os.path.exists(before_path):
                        with open(before_path, 'rb') as f:
                            slide.before_image.save(data["before_filename"], File(f), save=True)
                    if os.path.exists(after_path):
                        with open(after_path, 'rb') as f:
                            slide.after_image.save(data["after_filename"], File(f), save=True)

            else:
                if data.get("before_url"):
                    try:
                        req_before = urllib.request.Request(
                            data["before_url"],
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req_before, timeout=15) as resp:
                            slide.before_image.save(
                                f"slide_{data['order']}_before.jpg",
                                ContentFile(resp.read()),
                                save=True
                            )
                    except Exception as e:
                        self.stderr.write(f"Error downloading before image for {data['title']}: {e}")

                if data.get("after_url"):
                    try:
                        req_after = urllib.request.Request(
                            data["after_url"],
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req_after, timeout=15) as resp:
                            slide.after_image.save(
                                f"slide_{data['order']}_after.jpg",
                                ContentFile(resp.read()),
                                save=True
                            )
                    except Exception as e:
                        self.stderr.write(f"Error downloading after image for {data['title']}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {BeforeAfterSlide.objects.count()} sliders."))
