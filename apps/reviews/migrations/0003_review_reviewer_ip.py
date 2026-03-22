from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0002_review_approved_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="reviewer_ip",
            field=models.GenericIPAddressField(blank=True, editable=False, null=True),
        ),
    ]
