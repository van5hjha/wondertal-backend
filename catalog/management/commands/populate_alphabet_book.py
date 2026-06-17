import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from catalog.models import Product, BookTemplate, PageTemplate

PAGES_DATA = {
    "A": ("apple", "A is for apple. The toddler boy picks a big, shiny red apple from a low branch of a clay tree."),
    "B": ("bear", "B is for bear. The toddler boy hugs a friendly, big brown teddy bear."),
    "C": ("castle", "C is for castle. The toddler boy builds a colorful, whimsical toy castle out of clay blocks."),
    "D": ("dragon", "D is for dragon. The toddler boy feeds a friendly green baby dragon a piece of fruit."),
    "E": ("explorer", "E is for explorer. The toddler boy chases a large, colorful butterfly with a butterfly net."),
    "F": ("firefighter", "F is for firefighter. The toddler boy wears a firefighter helmet and sprays a tiny stream of water from a toy hose."),
    "G": ("gardener", "G is for gardener. The toddler boy waters a magical glowing flower with a small watering can."),
    "H": ("helicopter", "H is for helicopter. The toddler boy happily turns the steering wheel inside a colorful toy helicopter cockpit."),
    "I": ("ice_cream", "I is for ice cream. The toddler boy happily eats a giant multi-scoop ice cream cone, with a bit of ice cream on his nose."),
    "J": ("jester", "J is for jester. The toddler boy throws and catches three glowing sparkling balls, juggling them."),
    "K": ("kangaroo", "K is for kangaroo. The toddler boy jumps up and down happily next to a friendly mother kangaroo."),
    "L": ("lion", "L is for lion. The toddler boy gently brushes the soft fluffy mane of a friendly big lion."),
    "M": ("magician", "M is for magician. The toddler boy waves a magic wand and pulls a cute white rabbit out of a top hat."),
    "N": ("ninja", "N is for ninja. The toddler boy does a martial arts kick in a cute blue ninja suit."),
    "O": ("owl", "O is for owl. The toddler boy reads a colorful picture book to a wise friendly owl sitting next to him."),
    "P": ("pirate", "P is for pirate. The toddler boy spins a large ship steering wheel on a friendly pirate deck."),
    "Q": ("quokka", "Q is for quokka. The toddler boy takes a selfie next to a smiling quokka, both looking at the camera."),
    "R": ("robot", "R is for robot. The toddler boy high-fives a friendly colorful toy robot."),
    "S": ("submarine", "S is for submarine. The toddler boy looks through a round glass window of a submarine and waves at a passing friendly turtle."),
    "T": ("treasure", "T is for treasure. The toddler boy pulls a sparkling toy out of a glowing wooden treasure chest."),
    "U": ("unicorn", "U is for unicorn. The toddler boy brushes the pastel rainbow mane of a gentle white unicorn."),
    "V": ("volcano", "V is for volcano. The toddler boy catches colorful bubbles erupting from a friendly cartoon volcano."),
    "W": ("wizard", "W is for wizard. The toddler boy waves a star-topped wand, casting a spell that makes stars float in the air."),
    "X": ("xylophone", "X is for xylophone. The toddler boy taps keys on a giant colorful xylophone with mallets, looking happy."),
    "Y": ("yo_yo", "Y is for yo-yo. The toddler boy throws a glowing neon yo-yo down and watches it spin."),
    "Z": ("zoo", "Z is for zoo. The toddler boy waves happily to a tall giraffe that is leaning down to look at him near the zoo gate.")
}

class Command(BaseCommand):
    help = 'Populate the database with the Alphabet Book Product, BookTemplate, and PageTemplates.'

    def handle(self, *args, **options):
        self.stdout.write("Starting database population for Alphabet Book...")

        # 1. Get or Create Product
        product, p_created = Product.objects.get_or_create(
            slug="personalized-alphabet-book",
            defaults={
                "title": "Personalized Alphabet Book",
                "description": "A beautifully illustrated, personalized A to Z alphabet book featuring your child embarking on fun adventures for every letter.",
                "price": 19.99,
                "is_active": True
            }
        )
        if p_created:
            self.stdout.write(f"Created Product: '{product.title}'")
        else:
            self.stdout.write(f"Product already exists: '{product.title}'")

        # 2. Get or Create BookTemplate
        book_template, bt_created = BookTemplate.objects.get_or_create(
            product=product,
            title="Personalized Alphabet Book",
            defaults={
                "description": "A custom alphabet book featuring 3D claymation style illustrations for all 26 letters.",
                "age_group": "2-5",
                "is_active": True
            }
        )
        if bt_created:
            self.stdout.write(f"Created BookTemplate: '{book_template.title}'")
        else:
            self.stdout.write(f"BookTemplate already exists: '{book_template.title}'")

        # 3. Source directory for images
        source_dir = os.path.join(settings.BASE_DIR, 'alphabet_book')
        if not os.path.isdir(source_dir):
            self.stderr.write(f"Error: Source directory '{source_dir}' does not exist.")
            return

        # 4. Save Cover image if present
        cover_path = os.path.join(source_dir, 'Cover.png')
        if os.path.exists(cover_path):
            self.stdout.write("Saving cover image for BookTemplate...")
            with open(cover_path, 'rb') as f:
                book_template.cover_image.save('Cover.png', File(f), save=True)
            self.stdout.write("Cover image saved successfully.")
        else:
            self.stdout.write(self.style.WARNING("Warning: Cover.png not found in alphabet_book folder."))

        # 5. Save pages
        alphabet = sorted(PAGES_DATA.keys())
        for index, letter in enumerate(alphabet, start=1):
            keyword, story_text = PAGES_DATA[letter]
            page_number = index
            is_preview = page_number <= 3  # First 3 pages are previews

            # Get or create PageTemplate
            page_template, page_created = PageTemplate.objects.get_or_create(
                book_template=book_template,
                page_number=page_number,
                defaults={
                    "story_text": story_text,
                    "is_preview": is_preview
                }
            )

            # Update fields if already exists to ensure fresh copy
            if not page_created:
                page_template.story_text = story_text
                page_template.is_preview = is_preview

            img_filename = f"{letter}_{keyword}.png"
            mask_filename = f"{letter}_{keyword}_mask.png"

            page_template.image_name = img_filename
            page_template.mask_image_name = mask_filename
            page_template.save()

            action = "Created" if page_created else "Updated"
            self.stdout.write(f"[{letter}] {action} Page {page_number} ('{keyword}') with image_name '{img_filename}' and mask_image_name '{mask_filename}'.")

        self.stdout.write(self.style.SUCCESS("Alphabet Book database population completed successfully!"))
