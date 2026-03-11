import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.locations.models import Country


class Command(BaseCommand):
    help = "Populates the database with initial shared data"

    def handle(self, *args, **options):
        fixture_path = Path(settings.BASE_DIR) / "fixtures" / "countries.json"

        if not fixture_path.exists():
            self.stderr.write(self.style.ERROR(f"Fixture not found: {fixture_path}"))
            return

        with fixture_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        countries = [
            Country(
                country_code=(item["fields"].get("country_code") or "").strip().upper(),
                name=item["fields"].get("name", ""),
                region=item["fields"].get("region") or None,
                subregion=item["fields"].get("subregion", ""),
                business_region=item["fields"].get("business_region", ""),
            )
            for item in payload
            if item.get("model") == "locations.country"
            and (item.get("fields") or {}).get("country_code")
        ]

        Country.objects.bulk_create(
            countries,
            update_conflicts=True,
            unique_fields=["country_code"],
            update_fields=["name", "region", "subregion", "business_region"],
        )

        self.stdout.write(
            self.style.SUCCESS(f"Countries sync complete. {len(countries)} records processed.")
        )
