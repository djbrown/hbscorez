# Generated by Django 5.0.3 on 2024-03-26 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("associations", "0002_association_source_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Club",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.TextField(unique=True)),
                ("bhv_id", models.IntegerField(unique=True)),
                ("associations", models.ManyToManyField(to="associations.association")),
            ],
        ),
    ]