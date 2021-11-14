from django.contrib import admin

from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ('name', 'short_name', 'bhv_id')
