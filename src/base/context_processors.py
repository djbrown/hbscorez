from django.conf import settings


def matomo(request):
    return {'MATOMO_URL': settings.MATOMO_URL}
