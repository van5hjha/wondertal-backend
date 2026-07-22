import os
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
from catalog.models import Product, BookTemplate, ProductPreviewImage, ProductPreviewItem, PageTemplate

PRODUCTS_DATA = [
    {
        "slug": "personalized-alphabet-book",
        "title": "Personalized Alphabet Book",
        "category": "storybook",
        "description": "A beautifully illustrated, personalized A to Z alphabet book featuring your child embarking on fun adventures for every letter.",
        "age_range": "3-8 yrs",
        "rating": 4.9,
        "review_count": 120,
        "price_hardcover": 1499,
        "price_softcover": 999,
        "original_price_softcover": 1499,
        "original_price_hardcover": 1999,
        "features": ["26 Custom Illustrated Pages", "High-res Face Mapping", "Printed in India (7 day ship)"],
        "tags": ["Learning", "Creativity", "Fun"],
        "preview_images": [
            "assets/images/before_image.png"
        ],
        "template": {
            "title": "Personalized Alphabet Book",
            "description": "A custom alphabet book featuring 3D claymation style illustrations for all 26 letters.",
            "age_group": "2-5"
        }
    },
    {
        "slug": "galactic-kid",
        "title": "The Galactic Kid",
        "category": "storybook",
        "description": "An interstellar journey to save the Stardust Star. Perfect for dreamers.",
        "age_range": "3-8 yrs",
        "rating": 4.9,
        "review_count": 120,
        "price_hardcover": 1499,
        "price_softcover": 999,
        "original_price_softcover": 1499,
        "original_price_hardcover": 1999,
        "features": ["28 Custom Illustrated Pages", "High-res Face Mapping", "Printed in India (7 day ship)"],
        "tags": ["Persistence", "Kindness", "Curiosity"],
        "preview_images": [
            "assets/images/galactic_cover.png",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuDFLtaGpNexdOSZrynMkKr5QiGWyQ9UbV626c_wZw1ZCPwgBwUX1hWm0sc1PnkUCjmaT5ZGBXnOJGZpe-GZv5gt1rysaHMPDwLj_u-l6mbEV2IpVZX6I-xWBBbU0msPLSu9Bcf3sFjrPWKfD_AD8-gAFyaCAqDrwPvL0hSGcTxSKuMH80o0NPM9f9ZroNw--_p1uUsecJQPcZdyOmOR68qbbjQahLC73LxuDMrC035QzSxvcEqcUZGSvAm09SerjGAnr6JeuBhdjTs",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuD0ggPv8jvrTQOkFB3ZF3iRoKhSk_jg7mdhjjC_f5_BI6p1i8tnuvYxbUmCipN-oQC1u61TryhXBM-UV12J5SHl5_wecHXvNTMezbiZyEwa8Llw1GaDX8yjWqnknm8MG_MHDG348wsTdpdkCo8ks_Th4Z8QW8M-z-oGqgs0_wJSKN0BQpDKYLFwZrGLGkVPD1q3Wv1w3qRwXzTN5FHxJ1x0udzwbiqKPzLrCYb_brIYB0O2ZqpUT1763zIni-dv9TCRFdOzVQmU94Q",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuCGCUNadGyYSg2VSR7EK9k3sAyIHAlQwtbTg9QrT8WC6WHJrlDyojYZEL094n1T7-hA6dO3SF_PbxJoDcougllEXFX7GupenRW4GXCJHB_ilJT0NTmv4d97v0Wsau9fxUWCUIMVfZKPv3oK8VzeJP0iq8kSC8KiIyH-71LDuGcku-RnThnKVPtwPUeLm9aaM4XA5VZMgkIlJbIUBpYCtf3ax1D2DQg6c9KyiC1QKsnimCjX08NGr9tjz8kVaY815TTpRQUcpu559DU",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuBHbAK_cVio6utEDPailYl1_ziEgDacRBkNMMH6B_GoZf7KADBeOPVx6_qb8cbJtyU6N8YrSCSjlnWbghWsPG22M05B8eNVjGGtSknvqRC_duGG4Jqx3VuEhHXfJCqW6N6Y7crk7n4875CmccKANImBM8JcY23-nZSi0CAb_zFZEtk5CGiRz-NxNAQgyJ1QRFI88AyRbh7c7A08tK3Y0EGhLLP7zSWyja1PGakav6ft14yfTkDBDZTht54HBgD2VNv1V1-YHCnRV2I"
        ],
        "template": {
            "title": "The Galactic Kid",
            "description": "An interstellar adventure where your child becomes the hero of the galaxy.",
            "age_group": "3-8"
        }
    },
    {
        "slug": "jurassic-friend",
        "title": "Jurassic Friend",
        "category": "storybook",
        "description": "Travel back in time to find the friendliest dinosaurs in the valley.",
        "age_range": "2-6 yrs",
        "rating": 4.8,
        "review_count": 94,
        "price_hardcover": 1499,
        "price_softcover": 999,
        "original_price_softcover": 1499,
        "original_price_hardcover": 1999,
        "features": ["24 Custom Illustrated Pages", "High-res Face Mapping", "Printed in India (7 day ship)"],
        "tags": ["Teamwork", "Bravery", "Friendship"],
        "preview_images": [
            "assets/images/jurassic_cover.png"
        ],
        "template": {
            "title": "Jurassic Friend",
            "description": "A dinosaur adventure where your child befriended the gentle giants.",
            "age_group": "2-6"
        }
    },
    {
        "slug": "wild-safari",
        "title": "Wild Safari Trip",
        "category": "storybook",
        "description": "A thrilling exploration through the deepest jungles to find the Golden Lion.",
        "age_range": "4-9 yrs",
        "rating": 4.9,
        "review_count": 156,
        "price_hardcover": 1499,
        "price_softcover": 999,
        "original_price_softcover": 1499,
        "original_price_hardcover": 1999,
        "features": ["26 Custom Illustrated Pages", "High-res Face Mapping", "Printed in India (7 day ship)"],
        "tags": ["Empathy", "Discovery", "Patience"],
        "preview_images": [
            "assets/images/safari_cover.png"
        ],
        "template": {
            "title": "Wild Safari Trip",
            "description": "An exciting African safari where your child encounters marvelous wildlife.",
            "age_group": "4-9"
        }
    },
    {
        "slug": "cosmic-memory-frame",
        "title": "Cosmic Memory Frame",
        "category": "frame",
        "description": "Turn your favorite moments into magical space artifacts.",
        "age_range": "All ages",
        "rating": 4.9,
        "review_count": 85,
        "price_hardcover": 0,
        "price_softcover": 1099,
        "original_price_softcover": 1299,
        "original_price_hardcover": 0,
        "features": ["Waterproof Printing", "Premium Wooden Frame", "Custom AI Galaxy Mapping"],
        "tags": ["Gratitude", "Creativity"],
        "preview_images": [
            "https://lh3.googleusercontent.com/aida-public/AB6AXuDmrejXDU-3DH3VZ6jvnww0MEK_sTmSDSsD8cgyi_DDOXkbZIRpn2iZIbeCiEh6hZYJuaBNdvg_o0miJ4c3faghNZC1ERy6aX9gnU0ibn8DRbw7yTxj_rJeZg_wCMR5lw624_KbvLPAmoR7GK0UD_53kfdTSxpzcHR1xyPPF3QNJI4a2zV1YPznKQpQjjoPTvrWlxTnNA_z1nArg8AHbX8u0JzPQ8doR3h4oND7dxQKmv8h0mATWyZB"
        ],
        "template": {
            "title": "Cosmic Memory Frame",
            "description": "A customized space-themed memory frame featuring your child.",
            "age_group": "All ages"
        }
    },
    {
        "slug": "stardust-sticker-pack",
        "title": "Stardust Sticker Pack",
        "category": "sticker",
        "description": "Durable, waterproof stickers featuring your child as the hero.",
        "age_range": "3-12 yrs",
        "rating": 4.8,
        "review_count": 142,
        "price_hardcover": 0,
        "price_softcover": 374,
        "original_price_softcover": 499,
        "original_price_hardcover": 0,
        "features": ["Waterproof & UV Resistant", "Vinyl Material", "Includes 15 Custom Stickers"],
        "tags": ["Self-Expression", "Fun"],
        "preview_images": [
            "https://lh3.googleusercontent.com/aida-public/AB6AXuBfvYakLsWO4lfiytNJCwqfd3C988ojziKsmAXhut5JqkjPCwYsTnm6VArY_pCk8ndNJBLwhqORnkE-buLGewcMgKz_Sv0yv-YI0JUiRuVXugAYVrH1CgGHdnDsRt_mgGcRC3RszMhFfNn3Yc1AfFEd9RMV5K5VF5rH_Z-HAtyU1sBMx4o55weG9AKeiEj2NJPe4VM_TJVJB6wDurIoK04pppbRocJON2_F6JdcYEkz5bpNj8w2hfvP"
        ],
        "template": {
            "title": "Stardust Sticker Pack",
            "description": "Customized cartoon stardust stickers featuring your child.",
            "age_group": "3-12"
        }
    },
    {
        "slug": "galactic-name-labels",
        "title": "Galactic Name Labels",
        "category": "label",
        "description": "Personalized labels for school gear that never get lost in orbit.",
        "age_range": "5-10 yrs",
        "rating": 4.7,
        "review_count": 99,
        "price_hardcover": 0,
        "price_softcover": 639,
        "original_price_softcover": 799,
        "original_price_hardcover": 0,
        "features": ["Scratch Resistant", "Super Sticky Glue", "Pack of 40 Labels"],
        "tags": ["Responsibility", "Organization"],
        "preview_images": [
            "https://lh3.googleusercontent.com/aida-public/AB6AXuBiH4JAp1i3KlSYauyvP8ya4BimL1SuCZIiLBi6wWIHues_m7Gt-ZS5v2uvtKEgvhslz_PCsDDgMRudL4dyqKZ2UJY9Cpp3DptQEU-82omZsr2hzRnXCEOEHEqzkkX81RL9O3XkcxCpD-SNYJW8Jrt4YlU4AXBExlHN2ZJ-eUYmwhH05SbmPgxlbXMTkYTdIRUiBa6eMgSiF3O53xLRURSNRAT4Y0pkz0-5AqEvbJAcu1yKyXuDyIhL"
        ],
        "template": {
            "title": "Galactic Name Labels",
            "description": "Customized school gear name labels featuring your child.",
            "age_group": "5-10"
        }
    }
]

class Command(BaseCommand):
    help = 'Populate the database with Wondertale products and templates matching frontend assets.'

    def handle(self, *args, **options):
        self.stdout.write("Starting catalog database seeding...")

        for data in PRODUCTS_DATA:
            # 1. Create or Update Product
            product, created = Product.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "description": data["description"],
                    "price": 14.99,  # placeholder base price
                    "is_active": True,
                    "age_range": data["age_range"],
                    "rating": data["rating"],
                    "review_count": data["review_count"],
                    "price_hardcover": data["price_hardcover"],
                    "price_softcover": data["price_softcover"],
                    "original_price_softcover": data.get("original_price_softcover", 1499),
                    "original_price_hardcover": data.get("original_price_hardcover", 1999),
                    "category": data.get("category", "storybook"),
                    "features": data.get("features", []),
                    "tags": data.get("tags", []),
                }
            )

            if not created:
                # Update attributes
                product.title = data["title"]
                product.description = data["description"]
                product.age_range = data["age_range"]
                product.rating = data["rating"]
                product.review_count = data["review_count"]
                product.price_hardcover = data["price_hardcover"]
                product.price_softcover = data["price_softcover"]
                product.original_price_softcover = data.get("original_price_softcover", 1499)
                product.original_price_hardcover = data.get("original_price_hardcover", 1999)
                product.category = data.get("category", "storybook")
                product.features = data.get("features", [])
                product.tags = data.get("tags", [])
                product.save()
                self.stdout.write(f"Updated Product: '{product.title}'")
            else:
                self.stdout.write(f"Created Product: '{product.title}'")

            # 2. Re-create Preview Items to ensure freshness
            product.preview_items.all().delete()
            frontend_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'frontend'))
            
            preview_item = ProductPreviewItem.objects.create(
                product=product,
                item_type='static',
                order=0
            )

            for idx, img_url in enumerate(data["preview_images"]):
                preview_image = ProductPreviewImage(
                    item=preview_item,
                    order=idx
                )
                
                if img_url.startswith('http'):
                    # Remote URL
                    try:
                        req = urllib.request.Request(
                            img_url,
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req, timeout=15) as resp:
                            filename = f"prod_{product.slug}_{idx}.jpg"
                            preview_image.image.save(filename, ContentFile(resp.read()), save=True)
                    except Exception as e:
                        self.stderr.write(f"Error downloading preview image {img_url}: {e}")
                else:
                    # Local asset relative to frontend
                    local_path = os.path.join(frontend_dir, img_url)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            filename = os.path.basename(local_path)
                            preview_image.image.save(filename, File(f), save=True)
                    else:
                        self.stderr.write(f"Local preview image not found at: {local_path}")
            self.stdout.write(f"  Populated {len(data['preview_images'])} preview image(s).")

            # 3. Create or Update BookTemplate
            template_data = data["template"]
            book_template, bt_created = BookTemplate.objects.get_or_create(
                product=product,
                defaults={
                    "title": template_data["title"],
                    "description": template_data["description"],
                    "age_group": template_data["age_group"],
                    "is_active": True
                }
            )

            if not bt_created:
                book_template.title = template_data["title"]
                book_template.description = template_data["description"]
                book_template.age_group = template_data["age_group"]
                book_template.save()
                self.stdout.write(f"  Updated BookTemplate: '{book_template.title}' (ID: {book_template.id})")
            else:
                self.stdout.write(f"  Created BookTemplate: '{book_template.title}' (ID: {book_template.id})")

            # 4. Create or Update PageTemplate (ensure at least 1 page for preview worker)
            page_template, pt_created = PageTemplate.objects.get_or_create(
                book_template=book_template,
                page_number=1,
                defaults={
                    "story_text": f"Your custom {product.title}!",
                    "is_preview": True
                }
            )
            if not pt_created:
                page_template.is_preview = True
                page_template.save()
                self.stdout.write(f"  Updated PageTemplate for '{book_template.title}'")
            else:
                self.stdout.write(f"  Created PageTemplate for '{book_template.title}'")

        self.stdout.write(self.style.SUCCESS("Catalog database seeding completed successfully!"))
