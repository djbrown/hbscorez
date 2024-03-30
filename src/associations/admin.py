from django.contrib import admin

from associations.models import Association

ASSOCIATION_SEARCH_FIELDS = ["name", "abbreviation", "bhv_id"]


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    search_fields = ASSOCIATION_SEARCH_FIELDS
