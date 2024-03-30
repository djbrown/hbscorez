from django.contrib import admin

from associations.admin import ASSOCIATION_SEARCH_FIELDS
from districts.models import District

DISTRICT_SEARCH_FIELDS = ["name", "bhv_id"] + ["associations__" + field for field in ASSOCIATION_SEARCH_FIELDS]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = DISTRICT_SEARCH_FIELDS
