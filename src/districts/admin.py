from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.forms import CheckboxSelectMultiple
from django.db import models

from associations.admin import ASSOCIATION_SEARCH_FIELDS

from districts.models import District

DISTRICT_SEARCH_FIELDS = ['name', 'bhv_id'] + \
    ['associations__' + field for field in ASSOCIATION_SEARCH_FIELDS]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('bhv_id', 'name', 'get_associations')
    list_display_links = ('bhv_id', 'name')
    search_fields = DISTRICT_SEARCH_FIELDS

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple}
    }

    @admin.display(description='Verband')
    def get_associations(self, obj: District) -> str:
        association_links = [
            format_html('<a href="{}">{}</a>', reverse('admin:associations_association_change', args=[a.pk]), a.name) for a in obj.associations.all()
            ]
        return ', '.join(association_links)



