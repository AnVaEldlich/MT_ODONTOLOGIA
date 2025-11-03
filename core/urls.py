from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('registerdoctor/', views.registerdoctor, name='registerdoctor'),
    path('pedircita/', views.pedircita, name='pedircita'),
    path('Tratamientos/', views.Tratamientos, name='Tratamientos'),
    path('clinicas/', views.clinicas, name='clinicas'),
    path('Blog/', views.Blog, name='Blog'),
]
