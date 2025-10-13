from django.conf import settings
from django.shortcuts import get_object_or_404, render

from associations.models import Association


def show_all(request):
    associations = Association.objects.all()
    return render(
        request,
        "associations/list.j2",
        {
            "associations": associations,
            "source_url": settings.HBNET_ROOT_URL + "/verbaende",
        },
    )


def detail(request, short_name):
    association = get_object_or_404(Association, short_name=short_name)
    return render(request, "associations/detail.j2", {"association": association})
