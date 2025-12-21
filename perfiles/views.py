from django.shortcuts import render

# Create your views here.

def perfil_paciente(request):
    return render(request, 'perfiles/perfiles_paciente.html')
