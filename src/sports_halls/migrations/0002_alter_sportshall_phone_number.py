# Generated by Django 5.1.3 on 2024-11-22 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sports_halls", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sportshall",
            name="phone_number",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]