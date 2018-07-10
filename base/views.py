from django.shortcuts import render


def view_home(request):
    return render(request, 'base/home.html')


def view_notice(request):
    return render(request, 'base/imprint.html')


def view_privacy(request):
    return render(request, 'base/privacy.html')


def view_contact(request):
    return render(request, 'base/contact.html')
