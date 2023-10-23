from django.contrib import admin

from sports_halls.models import SportsHall


@admin.register(SportsHall)
class SportsHallAdmin(admin.ModelAdmin):
    list_display = ('bhv_id', 'number', 'name', 'address', 'location')
    list_display_links = ('bhv_id', 'number', 'name')
    search_fields = ('bhv_id', 'number', 'name', 'address')

    
    @admin.display(description='Ort')
    def location(self, obj: SportsHall) -> str:
        return obj.address.rpartition(' ')[2]