"""
Management command to load test/dummy schematic data for development
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from apps.schematics.models import Schematic, Tag
import hashlib
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Load test/dummy schematics for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before loading',
        )

    def handle(self, *args, **options):
        self.stdout.write('Loading test schematics...')

        # Clear existing test data if requested
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            Schematic.objects.filter(title__startswith='[TEST]').delete()
            Tag.objects.filter(slug__startswith='test-').delete()
            User.objects.filter(username__startswith='testuser').delete()

        # Create test users
        test_users = []
        for i in range(1, 4):
            username = f'testuser{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'storage_quota': 1073741824,  # 1GB
                    'storage_used': 0
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created test user: {username}'))
            test_users.append(user)

        # Create test tags
        tag_names = [
            'medieval', 'modern', 'fantasy', 'redstone', 
            'house', 'castle', 'farm', 'city'
        ]
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            if created:
                self.stdout.write(f'Created tag: {tag_name}')
            tags.append(tag)

        # Test schematic data
        test_schematics = [
            {
                'title': '[TEST] Medieval Castle',
                'description': 'A magnificent medieval castle with towers, walls, and a courtyard. Perfect for survival worlds or roleplay servers.',
                'category': 'building',
                'minecraft_version': '1.20.1',
                'width': 64,
                'height': 45,
                'length': 64,
                'block_count': 15000,
                'tags': ['medieval', 'castle'],
                'download_count': 245,
                'view_count': 1230,
            },
            {
                'title': '[TEST] Modern Villa',
                'description': 'Luxurious modern villa with pool, multiple floors, and contemporary design. Includes interior decoration.',
                'category': 'building',
                'minecraft_version': '1.19.4',
                'width': 32,
                'height': 20,
                'length': 40,
                'block_count': 8500,
                'tags': ['modern', 'house'],
                'download_count': 189,
                'view_count': 892,
            },
            {
                'title': '[TEST] Redstone Calculator',
                'description': 'Fully functional redstone calculator capable of basic arithmetic operations. Great for learning redstone mechanics.',
                'category': 'redstone',
                'minecraft_version': '1.20.1',
                'width': 20,
                'height': 10,
                'length': 25,
                'block_count': 3200,
                'tags': ['redstone'],
                'download_count': 567,
                'view_count': 2341,
            },
            {
                'title': '[TEST] Fantasy Treehouse',
                'description': 'Magical treehouse nestled in giant oak trees. Features bridges, multiple rooms, and enchanting details.',
                'category': 'building',
                'minecraft_version': '1.19.2',
                'width': 28,
                'height': 35,
                'length': 28,
                'block_count': 6800,
                'tags': ['fantasy', 'house'],
                'download_count': 423,
                'view_count': 1567,
            },
            {
                'title': '[TEST] Automated Farm',
                'description': 'Fully automated crop farm with villager trading hall. Includes wheat, carrots, and potatoes.',
                'category': 'farm',
                'minecraft_version': '1.20.2',
                'width': 50,
                'height': 15,
                'length': 50,
                'block_count': 12000,
                'tags': ['redstone', 'farm'],
                'download_count': 891,
                'view_count': 3245,
            },
            {
                'title': '[TEST] Medieval Town Square',
                'description': 'Bustling medieval town square with market stalls, fountain, and surrounding buildings. Perfect centerpiece for any medieval build.',
                'category': 'building',
                'minecraft_version': '1.19.4',
                'width': 48,
                'height': 25,
                'length': 48,
                'block_count': 11500,
                'tags': ['medieval', 'city'],
                'download_count': 312,
                'view_count': 1089,
            },
            {
                'title': '[TEST] Sci-Fi Space Station',
                'description': 'Futuristic space station with docking bays, living quarters, and observation deck. Uses concrete and glass.',
                'category': 'building',
                'minecraft_version': '1.20.1',
                'width': 60,
                'height': 40,
                'length': 60,
                'block_count': 18000,
                'tags': ['modern', 'fantasy'],
                'download_count': 198,
                'view_count': 745,
            },
            {
                'title': '[TEST] Starter Cottage',
                'description': 'Cozy starter cottage perfect for new players. Simple design with all the essentials.',
                'category': 'building',
                'minecraft_version': '1.20.2',
                'width': 12,
                'height': 8,
                'length': 14,
                'block_count': 980,
                'tags': ['house'],
                'download_count': 1534,
                'view_count': 5678,
            },
        ]

        # Create test schematics
        created_count = 0
        for idx, schematic_data in enumerate(test_schematics):
            # Create a dummy file content
            file_content = f"Dummy schematic file for: {schematic_data['title']}\n"
            file_content += f"UUID: {uuid.uuid4()}\n"
            file_content = file_content.encode('utf-8')
            
            # Calculate hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Get or create schematic
            schematic, created = Schematic.objects.get_or_create(
                title=schematic_data['title'],
                owner=test_users[idx % len(test_users)],
                defaults={
                    'description': schematic_data['description'],
                    'category': schematic_data['category'],
                    'minecraft_version': schematic_data['minecraft_version'],
                    'width': schematic_data['width'],
                    'height': schematic_data['height'],
                    'length': schematic_data['length'],
                    'block_count': schematic_data['block_count'],
                    'file_size': len(file_content),
                    'file_hash': file_hash,
                    'scan_status': 'clean',
                    'is_public': True,
                    'download_count': schematic_data['download_count'],
                    'view_count': schematic_data['view_count'],
                }
            )
            
            if created:
                # Add dummy file
                filename = f"{slugify(schematic_data['title'])}.schematic"
                schematic.file.save(filename, ContentFile(file_content), save=True)
                
                # Add tags
                tag_objects = [tag for tag in tags if tag.name in schematic_data['tags']]
                schematic.tags.set(tag_objects)
                
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {schematic_data["title"]}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully loaded {created_count} test schematics!'))
        self.stdout.write(f'Test users: testuser1, testuser2, testuser3 (password: testpass123)')
        self.stdout.write(f'Tags created: {", ".join(tag_names)}')
