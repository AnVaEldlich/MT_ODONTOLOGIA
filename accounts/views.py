"""Account management views for patient and professional registration."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Paciente, Profesional, ClinicCenter
from django.contrib.auth import authenticate, login


def login_view(request):
    """Display the login page."""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("email"),
            password=request.POST.get("password")
        )

        if user is not None:
            login(request, user)
            return redirect('perfil')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html')


def register(request):
    """Handle patient registration."""
    if request.method == "POST":

        email = request.POST.get("email")
        id_number = request.POST.get("id_number")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect('register')
        
        if Paciente.objects.filter(id_number=id_number).exists():
            messages.error(request, "Patient already registered")
            return redirect('register')

        # 1. Obtener lista de condiciones marcadas
        conditions = request.POST.getlist("conditions[]")

        user = User.objects.create_user(
            username=email,  # o username separado
            email=email,
            password=request.POST.get("password"),
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name")
    )

        # 2. Crear el paciente con los booleanos correctos
        Paciente.objects.create(
            
            user=user,

            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            id_type = request.POST.get("id_type"),
            id_number = request.POST.get("id_number"),
            birth_date = request.POST.get("birth_date"),
            gender = request.POST.get("gender"),
            # email = request.POST.get("email"),
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

            # password = make_password(request.POST.get("password")),
        )

        

        login(request, user)

        return redirect('perfil')  # Redirige al perfil del paciente después del registro
    return render(request, 'accounts/register.html')


def registro_pro(request):
    """Display the professional registration page."""
    return render(request, 'accounts/registro_pro.html')


def registerprofesional(request):
    """Handle professional registration."""
    if request.method == 'POST':
        # Crear el usuario
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password1'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )
        
        # Crear el profesional
        Profesional.objects.create(
            user=user,
            id_type=request.POST['id_type'],
            id_number=request.POST['id_number'],
            especialidad=request.POST['especialidad'],
            ubicacion=request.POST['ubicacion'],
            codigo_pais=request.POST['codigo_pais'],
            telefono=request.POST['telefono']
        )

    return render(request, 'accounts/registerprofesional.html')


def formclinic(request):
    """Handle clinic center registration."""
    if request.method == "POST":
        # Crear el centro médico
        ClinicCenter.objects.create(
            clinic_name=request.POST.get("clinicName"),
            specialists_range=request.POST.get("specialists"),
            city=request.POST.get("city"),
        )
        messages.success(request, "Centro Médico registrado exitosamente.")
        return redirect('formclinic')

    return render(request, 'accounts/formclinic.html')