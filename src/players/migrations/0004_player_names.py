import logging

import django.db.models.deletion
from django.db import migrations, models

LOGGER = logging.getLogger("hbscorez")


class Migration(migrations.Migration):
    dependencies = [
        ("players", "0003_reportsblacklist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="score",
            name="player",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="players.player",
            ),
        ),
        migrations.AlterField(
            model_name="score",
            name="player_number",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="score",
            name="goals",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="score",
            name="penalty_goals",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="score",
            name="penalty_tries",
            field=models.IntegerField(default=0),
        ),
    ]
