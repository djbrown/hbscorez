from django.shortcuts import render

from .models import Association


def index(request):
    associations = Association.objects.all()
    return render(request, 'scorers/index.html', {'associations': associations})


def association_overview(request, assoc_abbr):
    association = Association.objects.filter(abbreviation__iexact=assoc_abbr).first()
    return render(request, 'associations/association.html', {'association': association})
