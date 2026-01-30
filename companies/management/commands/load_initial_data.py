from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Populates the database with initial data"

    def handle(self, *args, **options):
        call_command('loaddata', 'fixtures/countries.json')
