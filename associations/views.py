from django.shortcuts import render

from .models import Association


def associations(request):
    assocs = Association.objects.all()
    return render(request, 'scorers/index.html', {'associations': assocs})


def association(request, assoc_abbr):
    assoc = Association.objects.filter(abbreviation__iexact=assoc_abbr).first()
    return render(request, 'associations/association.html', {'association': assoc})
