from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.admin_panel.models import AdminUser

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin superuser'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Admin username')
        parser.add_argument('email', type=str, help='Admin email')
        parser.add_argument('password', type=str, help='Admin password')
        parser.add_argument('--phone', type=str, default='+254700000000', help='Admin phone number')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        phone = options['phone']

        try:
            # Check if admin already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists'))
                return

            # Create Django user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True,
            )

            # Create AdminUser profile
            admin_profile = AdminUser.objects.create(
                user=user,
                role='superadmin',
                is_active=True,
                can_suspend_users=True,
                can_adjust_transactions=True,
                can_verify_kyc=True,
                can_manage_admins=True,
            )

            self.stdout.write(self.style.SUCCESS(f'✓ Admin user "{username}" created successfully!'))
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Role: Super Admin')
            self.stdout.write(f'  All permissions enabled')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating admin: {str(e)}'))
