# Generated by Django 4.2.4 on 2023-10-23 20:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "districts",
            "0002_alter_district_options_alter_district_associations_and_more",
        ),
        ("leagues", "0003_leaguename"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="league",
            options={"verbose_name": "Liga", "verbose_name_plural": "Ligen"},
        ),
        migrations.AlterModelOptions(
            name="season",
            options={
                "ordering": ("start_year",),
                "verbose_name": "Saison",
                "verbose_name_plural": "Saisons",
            },
        ),
        migrations.AlterField(
            model_name="league",
            name="abbreviation",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="league",
            name="bhv_id",
            field=models.IntegerField(unique=True, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="league",
            name="district",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="districts.district",
                verbose_name="Bezirk",
            ),
        ),
        migrations.AlterField(
            model_name="league",
            name="name",
            field=models.CharField(max_length=255, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="league",
            name="season",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="leagues.season",
                verbose_name="Saison",
            ),
        ),
    ]