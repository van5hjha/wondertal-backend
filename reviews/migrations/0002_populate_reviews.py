# Generated manually on 2026-06-13

from django.db import migrations

def populate_reviews(apps, schema_editor):
    Review = apps.get_model('reviews', 'Review')
    
    reviews_data = [
        # Row 1 Reviews
        {
            "quote": "Seeing my son Aarav's face on the space explorer cover was priceless! He now reads it every single night.",
            "name": "Priya Sharma",
            "location": "Mumbai, Maharashtra",
            "rating": 5,
        },
        {
            "quote": "The quality is amazing, a forever keepsake. The AI matched my daughter's curls perfectly!",
            "name": "Rajesh Patel",
            "location": "Bengaluru, Karnataka",
            "rating": 5,
        },
        {
            "quote": "Best birthday gift ever. My nephew thinks he is a real superhero. Highly recommend to all parents!",
            "name": "Sunita Rao",
            "location": "Hyderabad, Telangana",
            "rating": 5,
        },
        {
            "quote": "I was skeptical about AI, but the art style is breathtaking. The stories are genuinely interesting too.",
            "name": "Amit Verma",
            "location": "Delhi, NCR",
            "rating": 5,
        },
        {
            "quote": "Got the hardcover for my son's 5th birthday. The print quality and paper thickness is outstanding.",
            "name": "Vikram Malhotra",
            "location": "Pune, Maharashtra",
            "rating": 5,
        },
        # Row 2 Reviews
        {
            "quote": "The process was so simple! Just uploaded a photo and got a preview in 2 minutes. Excellent service.",
            "name": "Deepa Nair",
            "location": "Kochi, Kerala",
            "rating": 5,
        },
        {
            "quote": "My daughter started jumping with joy when she saw herself as a little wizard. Super happy!",
            "name": "Sanjay Gupta",
            "location": "Kolkata, West Bengal",
            "rating": 5,
        },
        {
            "quote": "Outstanding storytelling and beautiful illustrations. It's not just a gimmick, it's a high-quality book.",
            "name": "Meenakshi Sundaram",
            "location": "Chennai, Tamil Nadu",
            "rating": 5,
        },
        {
            "quote": "The custom text options and easy checkout made this a great gifting experience. Will order again!",
            "name": "Anil Deshmukh",
            "location": "Nagpur, Maharashtra",
            "rating": 5,
        },
        {
            "quote": "A wonderful personalized gift that kids will treasure forever. Absolute value for money.",
            "name": "Karan Joshi",
            "location": "Ahmedabad, Gujarat",
            "rating": 5,
        },
    ]

    for data in reviews_data:
        Review.objects.create(**data)

def unload_reviews(apps, schema_editor):
    Review = apps.get_model('reviews', 'Review')
    Review.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_reviews, unload_reviews),
    ]
