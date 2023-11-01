from django.db import migrations

from base.logic import delete_noname_players


class Migration(migrations.Migration):
    dependencies = [
        ("players", "0004_player_names_structure"),
    ]

    operations = [
        migrations.RunPython(delete_noname_players, elidable=True),
    ]
