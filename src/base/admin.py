from django.contrib import admin

from base.models import Env, GlobalMessage

admin.site.register(GlobalMessage)


@admin.register(Env)
class EnvAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
