from django.db import migrations

from base.logic import unify_player_names


class Migration(migrations.Migration):
    dependencies = [
        ("players", "0005_delete_nonames"),
    ]

    operations = [
        migrations.RunPython(unify_player_names, elidable=True),
    ]
