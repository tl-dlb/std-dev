from django.shortcuts import render, redirect


def home(request):
    return render(request, 'pages/home.html')

def handler403(request, exception):
    return render(request, 'pages/403.html', {'exception': exception})

def handler404(request, exception):
    return render(request, 'pages/404.html', {'exception': exception})
