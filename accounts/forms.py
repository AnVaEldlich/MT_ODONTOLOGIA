from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import ClinicCenter, Paciente, Profesional


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tu@email.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError("Credenciales inválidas.")
        return cleaned

    def get_user(self):
        return self.user_cache


class PatientRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    id_type = forms.CharField(max_length=20)
    id_number = forms.CharField(max_length=30)
    birth_date = forms.DateField()
    gender = forms.CharField(max_length=20)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    department = forms.CharField(max_length=50)
    emergency_contact = forms.CharField(max_length=100, required=False)
    emergency_phone = forms.CharField(max_length=20, required=False)
    eps = forms.CharField(max_length=100, required=False)
    medications = forms.CharField(required=False, widget=forms.Textarea)
    dental_history = forms.CharField(required=False, widget=forms.Textarea)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    conditions = forms.MultipleChoiceField(
        required=False,
        choices=[
            ("diabetes", "Diabetes"),
            ("hipertension", "Hipertensión"),
            ("cardiopatia", "Problemas cardíacos"),
            ("alergias", "Alergias"),
            ("embarazo", "Embarazo"),
            ("ninguna", "Ninguna"),
        ],
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data["id_number"]
        if Paciente.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Este documento ya está registrado.")
        return id_number

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        conditions = set(self.cleaned_data.get("conditions") or [])
        email = self.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )
        paciente = Paciente.objects.create(
            user=user,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            id_type=self.cleaned_data["id_type"],
            id_number=self.cleaned_data["id_number"],
            birth_date=self.cleaned_data["birth_date"],
            gender=self.cleaned_data["gender"],
            phone=self.cleaned_data["phone"],
            address=self.cleaned_data["address"],
            city=self.cleaned_data["city"],
            department=self.cleaned_data["department"],
            emergency_contact=self.cleaned_data.get("emergency_contact") or None,
            emergency_phone=self.cleaned_data.get("emergency_phone") or None,
            eps=self.cleaned_data.get("eps") or None,
            diabetes="diabetes" in conditions,
            hipertension="hipertension" in conditions,
            cardiopatia="cardiopatia" in conditions,
            alergias="alergias" in conditions,
            embarazo="embarazo" in conditions,
            ninguna="ninguna" in conditions,
            medications=self.cleaned_data.get("medications"),
            dental_history=self.cleaned_data.get("dental_history"),
        )
        from .roles import assign_paciente_group

        assign_paciente_group(user)
        return user, paciente


class ProfessionalRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    id_type = forms.ChoiceField(choices=Profesional.ID_TYPE_CHOICES)
    id_number = forms.CharField(max_length=30)
    especialidad = forms.ChoiceField(choices=Profesional.ESPECIALIDAD_CHOICES)
    ubicacion = forms.CharField(max_length=255)
    codigo_pais = forms.CharField(max_length=5, initial="+57")
    telefono = forms.CharField(max_length=20)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username

    def clean_id_number(self):
        id_number = self.cleaned_data["id_number"]
        if Profesional.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError("Este documento ya está registrado.")
        return id_number

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )
        profesional = Profesional.objects.create(
            user=user,
            id_type=self.cleaned_data["id_type"],
            id_number=self.cleaned_data["id_number"],
            especialidad=self.cleaned_data["especialidad"],
            ubicacion=self.cleaned_data["ubicacion"],
            codigo_pais=self.cleaned_data["codigo_pais"],
            telefono=self.cleaned_data["telefono"],
        )
        from .roles import assign_profesional_group

        assign_profesional_group(user)
        return user, profesional


class ClinicCenterForm(forms.ModelForm):
    class Meta:
        model = ClinicCenter
        fields = ("clinic_name", "specialists_range", "city")
        widgets = {
            "clinic_name": forms.TextInput(attrs={"name": "clinicName"}),
            "specialists_range": forms.Select(attrs={"name": "specialists"}),
            "city": forms.TextInput(attrs={"name": "city"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["clinic_name"].widget.attrs["name"] = "clinicName"
        self.fields["specialists_range"].widget.attrs["name"] = "specialists"
        self.fields["city"].widget.attrs["name"] = "city"
