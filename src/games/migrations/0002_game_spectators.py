# Generated by Django 2.1.5 on 2019-02-10 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="spectators",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
