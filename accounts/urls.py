from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("registro_pro/", views.registro_pro, name="registro_pro"),
    path("registerprofesional/", views.registerprofesional, name="registerprofesional"),
    path("formclinic/", views.formclinic, name="formclinic"),
]
