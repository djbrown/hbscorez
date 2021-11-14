from django.contrib import admin

from .models import SportsHall


@admin.register(SportsHall)
class SportsHallAdmin(admin.ModelAdmin):
    search_fields = ('number', 'name', 'address', 'bhv_id')
