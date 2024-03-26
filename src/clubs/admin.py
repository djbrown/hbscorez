from django.contrib import admin

from associations.admin import ASSOCIATION_SEARCH_FIELDS
from clubs.models import Club

CLUB_SEARCH_FIELDS = ['name', 'bhv_id'] + \
    ['association__' + field for field in ASSOCIATION_SEARCH_FIELDS]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    search_fields = CLUB_SEARCH_FIELDS
