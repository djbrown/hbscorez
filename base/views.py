from django.shortcuts import render


def home(request):
    return render(request=request, template_name='base/home.html')


def notice(request):
    return render(request=request, template_name='base/notice.html')


def contact(request):
    return render(request=request, template_name='base/contact.html')
