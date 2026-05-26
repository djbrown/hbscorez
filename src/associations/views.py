from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from associations.models import Association


@require_safe
def show_all(request):
    associations = Association.objects.all()
    return render(
        request,
        "associations/list.j2",
        {
            "associations": associations,
            "root_url": settings.NEW_ROOT_SOURCE_URL,
        },
    )


@require_safe
def detail(request, pk):
    association = get_object_or_404(Association, pk=pk)
    return render(request, "associations/detail.j2", {"association": association})
