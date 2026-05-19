from django.contrib import admin

from associations.models import Association

ASSOCIATION_SEARCH_FIELDS = ["name", "short_name", "abbreviation"]


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    search_fields = ASSOCIATION_SEARCH_FIELDS
