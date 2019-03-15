from django.shortcuts import render


def view_home(request):
    return render(request, 'base/home.j2')


def view_notice(request):
    return render(request, 'base/imprint.j2')


def view_privacy(request):
    return render(request, 'base/privacy.j2')


def view_contact(request):
    return render(request, 'base/contact.j2')
