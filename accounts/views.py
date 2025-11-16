from django.shortcuts import render

# Create your views here.

def login_view(request):

    return render(request, 'accounts/login.html')

def register(request):

    return render(request, 'accounts/register.html')

def registro_pro(request):

    return render(request, 'accounts/registro_pro.html')
