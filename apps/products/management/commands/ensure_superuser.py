from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Ensure a default superuser exists'

    def handle(self, *args, **options):
        phone = '9730531040'
        password = 'Admin@12345'

        # Check if superuser already exists
        if CustomUser.objects.filter(phone_number=phone).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser {phone} already exists'))
            return

        # Create superuser
        try:
            user = CustomUser.objects.create_superuser(
                phone_number=phone,
                full_name='Admin',
                user_type='seller',
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser created: {phone}'))
            self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))