from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Setup CMS groups with descriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all existing groups',
        )

    def handle(self, *args, **options):
        if options['list']:
            self._list_groups()
            return

        # Create the CMS groups
        groups_info = {
            'viewer': 'Can view all entries but cannot edit or publish',
            'editor': 'Can view and edit all entries but cannot publish',
            'publisher': 'Can view, edit, and publish all entries'
        }

        self.stdout.write(self.style.SUCCESS('Setting up CMS groups...\n'))

        for group_name, description in groups_info.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created group: {group_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Group already exists: {group_name}')
                )
            
            self.stdout.write(f'   📝 {description}\n')

        self.stdout.write(
            self.style.SUCCESS(
                '🎉 CMS groups setup complete!\n\n'
                'You can now assign users to groups using:\n'
                'python manage.py create_cms_user_with_group <username> <password> --group <group_name>\n\n'
                'Available groups: viewer, editor, publisher'
            )
        )

    def _list_groups(self):
        """List all existing groups"""
        groups = Group.objects.all().order_by('name')
        
        if not groups:
            self.stdout.write(self.style.WARNING('No groups found.'))
            return

        self.stdout.write(self.style.SUCCESS('📋 Existing groups:\n'))
        
        cms_groups = ['viewer', 'editor', 'publisher']
        
        for group in groups:
            if group.name in cms_groups:
                user_count = group.user_set.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {group.name} ({user_count} user{"s" if user_count != 1 else ""})'
                    )
                )
                
                # List users in group
                if user_count > 0:
                    users = list(group.user_set.values_list('username', flat=True))
                    self.stdout.write(f'   👥 Users: {", ".join(users)}')
                
                # Show permissions
                permissions = self._get_group_permissions(group.name)
                for perm in permissions:
                    self.stdout.write(f'   {perm}')
                self.stdout.write('')
            else:
                # Non-CMS group
                user_count = group.user_set.count()
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f'ℹ️  {group.name} ({user_count} user{"s" if user_count != 1 else ""}) - Custom group'
                    )
                )

    def _get_group_permissions(self, group_name):
        """Get permissions description for a group"""
        permissions = {
            'viewer': [
                '   📖 View all entries (published and unpublished)',
                '   📋 List entries',
                '   ❌ Cannot create, edit, delete, or publish'
            ],
            'editor': [
                '   📖 View all entries',
                '   📋 List entries',
                '   ➕ Create entries',
                '   ✏️  Edit any entry',
                '   🗑️  Delete any entry',
                '   ❌ Cannot publish entries'
            ],
            'publisher': [
                '   📖 View all entries',
                '   📋 List entries',
                '   ➕ Create entries',
                '   ✏️  Edit any entry',
                '   🗑️  Delete any entry',
                '   🚀 Publish/unpublish any entry'
            ]
        }
        return permissions.get(group_name, [])
