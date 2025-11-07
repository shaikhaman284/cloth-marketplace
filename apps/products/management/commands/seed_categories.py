from django.core.management.base import BaseCommand
from apps.products.models import Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Seed initial product categories'

    def handle(self, *args, **kwargs):
        categories_data = [
            {
                'name': "Men's Wear",
                'subcategories': ['Shirts', 'T-Shirts', 'Pants', 'Jeans', 'Kurtas', 'Ethnic Wear']
            },
            {
                'name': "Women's Wear",
                'subcategories': ['Sarees', 'Kurtis', 'Salwar Suits', 'Dresses', 'Tops', 'Ethnic Wear', 'Western Wear']
            },
            {
                'name': "Kids Wear",
                'subcategories': ['Boys', 'Girls', 'Infants']
            },
            {
                'name': "Accessories",
                'subcategories': ['Bags', 'Belts', 'Wallets', 'Scarves', 'Jewelry']
            },
        ]

        for idx, cat_data in enumerate(categories_data):
            # Create parent category
            parent, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'display_order': idx + 1,
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {parent.name}'))

            # Create subcategories
            for sub_idx, sub_name in enumerate(cat_data['subcategories']):
                sub, sub_created = Category.objects.get_or_create(
                    name=sub_name,
                    parent=parent,
                    defaults={
                        'slug': slugify(f"{parent.name}-{sub_name}"),
                        'display_order': sub_idx + 1,
                        'is_active': True
                    }
                )

                if sub_created:
                    self.stdout.write(self.style.SUCCESS(f'  - Created subcategory: {sub.name}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Categories seeded successfully!'))