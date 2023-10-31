from django.contrib import admin

from associations.models import Association

ASSOCIATION_SEARCH_FIELDS = ['name', 'abbreviation', 'bhv_id']


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ['bhv_id', 'abbreviation', 'name']
    search_fields = ['name', 'abbreviation', 'bhv_id']
