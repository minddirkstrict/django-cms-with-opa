from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Create a CMS user and assign them to a group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('password', type=str, help='Password for the new user')
        parser.add_argument(
            '--group',
            type=str,
            choices=['viewer', 'editor', 'publisher'],
            help='Group to assign the user to (viewer, editor, publisher)',
            default=None
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the new user (optional)',
            default=''
        )
        parser.add_argument(
            '--staff',
            action='store_true',
            help='Make the user a staff member (overrides group permissions)',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        group_name = options['group']
        is_staff = options['staff']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists!')
            )
            return

        # Create the user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                is_staff=is_staff
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created user "{username}"')
            )
            
            if is_staff:
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is staff - has admin permissions')
                )
            
            # Assign to group if specified
            if group_name:
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created group "{group_name}"')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Added user "{username}" to group "{group_name}"')
                )
                
                # Display group permissions
                self._display_group_permissions(group_name)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'User "{username}" has default permissions (read-only - can only list entries)'
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\nUser can now log in at: http://localhost:8000/cms/login/'
                )
            )
            
        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )

    def _display_group_permissions(self, group_name):
        """Display what permissions the group has"""
        permissions = {
            'viewer': [
                '✅ View all entries (published and unpublished)',
                '✅ List entries',
                '❌ Cannot create, edit, delete, or publish entries'
            ],
            'editor': [
                '✅ View all entries (published and unpublished)',
                '✅ List entries',
                '✅ Create new entries',
                '✅ Edit any entry',
                '✅ Delete any entry',
                '❌ Cannot publish entries'
            ],
            'publisher': [
                '✅ View all entries (published and unpublished)',
                '✅ List entries', 
                '✅ Create new entries',
                '✅ Edit any entry',
                '✅ Delete any entry',
                '✅ Publish/unpublish any entry'
            ]
        }
        
        self.stdout.write(f'\n📋 Group "{group_name}" permissions:')
        for perm in permissions.get(group_name, []):
            self.stdout.write(f'  {perm}')
