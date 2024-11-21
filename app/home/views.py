from django.shortcuts import render

def index(request):
    return render(request, 'home/index.html')


def qr(request):
    return render(request, 'home/qr.html')


def about(request):
    return render(request, 'home/about.html')