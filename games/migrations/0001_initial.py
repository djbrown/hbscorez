# Generated by Django 2.1.1 on 2018-09-14 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('leagues', '0001_initial'),
        ('sports_halls', '0001_initial'),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
                ('opening_whistle', models.DateTimeField(blank=True, null=True)),
                ('home_goals', models.IntegerField(blank=True, null=True)),
                ('guest_goals', models.IntegerField(blank=True, null=True)),
                ('report_number', models.IntegerField(blank=True, null=True, unique=True)),
                ('forfeiting_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forfeiting_team', to='teams.Team')),
                ('guest_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_team', to='teams.Team')),
                ('home_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='teams.Team')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.League')),
                ('sports_hall', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sports_halls.SportsHall')),
            ],
        ),
    ]
