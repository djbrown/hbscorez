from django.contrib import admin

from .models import Score, Team, Game, Player

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Score)
