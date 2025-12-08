"""
Management command to create a default admin user for testing and development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a default admin user for testing and development'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'
        email = 'admin@local.test'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists.')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        
        # Set role if the model has it
        if hasattr(user, 'role'):
            user.role = 'ADMIN'
            user.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'  Username: {username}\n'
                f'  Password: {password}\n'
                f'  Email: {email}\n'
            )
        )
