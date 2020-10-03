from django.contrib import admin

from .models import Env, GlobalMessage

admin.site.register(Env)
admin.site.register(GlobalMessage)
