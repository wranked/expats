from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0015_company_approved_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="created_via",
            field=models.CharField(
                choices=[
                    ("USER", "User"),
                    ("SCRIPT", "Script"),
                    ("IMPORT", "Import"),
                    ("ADMIN", "Admin"),
                    ("API", "API"),
                ],
                default="API",
                max_length=20,
            ),
        ),
    ]
