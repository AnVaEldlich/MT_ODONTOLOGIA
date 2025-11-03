from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'pages/about.html')

def register(request):
    return render(request, 'pages/register.html')

def login(request):
    return render(request, 'pages/TheHome.html')

def registerdoctor(request):
    return render(request, 'pages/registerdoctor.html')

def pedircita(request):
    return render(request, 'pages/pedircita.html')

def Tratamientos(request):
    return render(request, 'pages/Tratamientos.html')

def clinicas(request):
    return render(request, 'pages/clinicas.html')

def Blog(request):
    return render(request, 'pages/Blog.html')
