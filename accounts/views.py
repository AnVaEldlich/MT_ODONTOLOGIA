from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import Paciente

# Create your views here.

def login_view(request):

    return render(request, 'accounts/login.html')

def register(request):

    if request.method == "POST":
        
        # 1. Obtener lista de condiciones marcadas
        conditions = request.POST.getlist("conditions[]")

        # 2. Crear el paciente con los booleanos correctos
        Paciente.objects.create(
            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            id_type = request.POST.get("id_type"),
            id_number = request.POST.get("id_number"),
            birth_date = request.POST.get("birth_date"),
            gender = request.POST.get("gender"),
            email = request.POST.get("email"),
            phone = request.POST.get("phone"),
            address = request.POST.get("address"),
            city = request.POST.get("city"),
            department = request.POST.get("department"),
            emergency_contact = request.POST.get("emergency_contact"),
            emergency_phone = request.POST.get("emergency_phone"),
            eps = request.POST.get("eps"),

            # Checkbox convertidos correctamente
            diabetes = "diabetes" in conditions,
            hipertension = "hipertension" in conditions,
            cardiopatia = "cardiopatia" in conditions,
            alergias = "alergias" in conditions,
            embarazo = "embarazo" in conditions,
            ninguna = "ninguna" in conditions,

            medications = request.POST.get("medications"),
            dental_history = request.POST.get("dental_history"),

            password = make_password(request.POST.get("password")),
        )

        return redirect('login')
        
    return render(request, 'accounts/register.html')

def registro_pro(request):

    return render(request, 'accounts/registro_pro.html')

def registerprofesional(request):
    return render(request, 'accounts/registerprofesional.html')

def formclinic(request):
    return render(request, 'accounts/formclinic.html')
