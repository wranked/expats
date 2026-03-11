from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Populates the database with initial shared data"

    def handle(self, *args, **options):
        call_command("loaddata", "fixtures/countries.json")
