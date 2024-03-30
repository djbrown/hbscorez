from django.conf import settings


def matomo(_request):
    return {"MATOMO_URL": settings.MATOMO_URL}
