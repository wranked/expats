from django.db import migrations, models


def ensure_branch_addresses(apps, schema_editor):
    Branch = apps.get_model("companies", "Branch")
    Address = apps.get_model("locations", "Address")

    for branch in Branch.objects.filter(address__isnull=True, location__isnull=False):
        address = Address.objects.create(
            name=branch.name,
            street="",
            number="",
            postal_code="",
            location_id=branch.location_id,
        )
        branch.address_id = address.id
        branch.save(update_fields=["address"])


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("companies", "0021_company_primary_location"),
    ]

    operations = [
        migrations.RunPython(ensure_branch_addresses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="branch",
            name="address",
            field=models.OneToOneField(on_delete=models.CASCADE, to="locations.address"),
        ),
        migrations.RemoveField(
            model_name="branch",
            name="location",
        ),
    ]
