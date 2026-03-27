from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.

@login_required
def perfil_paciente(request):
    return render(request, 'perfiles/perfiles_paciente.html')
