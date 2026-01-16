"""
Management command to clear test/dummy schematic data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.schematics.models import Schematic, Tag, SchematicComment, SchematicLike

User = get_user_model()


class Command(BaseCommand):
    help = 'Clear test/dummy schematics and related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all schematics, not just test data',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Clear ALL schematic data (use with caution!)
            self.stdout.write(self.style.WARNING('Clearing ALL schematic data...'))
            
            # Get counts before deletion
            schematic_count = Schematic.objects.count()
            comment_count = SchematicComment.objects.count()
            like_count = SchematicLike.objects.count()
            tag_count = Tag.objects.count()
            
            # Delete all
            SchematicComment.objects.all().delete()
            SchematicLike.objects.all().delete()
            Schematic.objects.all().delete()
            Tag.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS(f'Deleted {schematic_count} schematics'))
            self.stdout.write(self.style.SUCCESS(f'Deleted {comment_count} comments'))
            self.stdout.write(self.style.SUCCESS(f'Deleted {like_count} likes'))
            self.stdout.write(self.style.SUCCESS(f'Deleted {tag_count} tags'))
        else:
            # Clear only test data
            self.stdout.write('Clearing test schematic data...')
            
            # Get test schematics
            test_schematics = Schematic.objects.filter(title__startswith='[TEST]')
            schematic_count = test_schematics.count()
            
            # Delete related data first
            comment_count = SchematicComment.objects.filter(schematic__in=test_schematics).count()
            like_count = SchematicLike.objects.filter(schematic__in=test_schematics).count()
            
            SchematicComment.objects.filter(schematic__in=test_schematics).delete()
            SchematicLike.objects.filter(schematic__in=test_schematics).delete()
            
            # Delete test schematics
            test_schematics.delete()
            
            # Delete test tags (only if no other schematics use them)
            test_tags = Tag.objects.filter(slug__startswith='test-')
            tag_count = 0
            for tag in test_tags:
                if tag.schematics.count() == 0:
                    tag.delete()
                    tag_count += 1
            
            # Optionally delete test users (only if they have no other schematics)
            test_users = User.objects.filter(username__startswith='testuser')
            user_count = 0
            for user in test_users:
                if user.schematics.count() == 0:
                    user.delete()
                    user_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Deleted {schematic_count} test schematics'))
            self.stdout.write(self.style.SUCCESS(f'Deleted {comment_count} comments'))
            self.stdout.write(self.style.SUCCESS(f'Deleted {like_count} likes'))
            if tag_count > 0:
                self.stdout.write(self.style.SUCCESS(f'Deleted {tag_count} unused test tags'))
            if user_count > 0:
                self.stdout.write(self.style.SUCCESS(f'Deleted {user_count} test users'))
        
        self.stdout.write(self.style.SUCCESS('\nTest data cleared successfully!'))
