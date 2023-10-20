from django.conf import settings
from django.shortcuts import get_object_or_404, render

from associations.models import Association


def show_all(request):
    associations = Association.objects.all()
    return render(request, 'associations/list.j2',
                  {'associations': associations,
                   'root_url': settings.NEW_ROOT_SOURCE_URL})


def detail(request, bhv_id):
    association = get_object_or_404(Association, bhv_id=bhv_id)
    return render(request, 'associations/detail.j2', {'association': association})
