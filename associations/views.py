from django.shortcuts import render, get_object_or_404

from .models import Association


def list(request):
    associations = Association.objects.all()
    return render(request, 'associations/list.html', {'associations': associations})


def detail(request, bhv_id):
    association = get_object_or_404(Association, bhv_id=bhv_id)
    return render(request, 'associations/detail.html', {'association': association})
