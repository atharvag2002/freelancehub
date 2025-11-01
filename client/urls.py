from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    path('register/', views.client_register, name='register'),
    path('login/', views.client_login, name='login'),
    path('logout/', views.client_logout, name='logout'),
    path('dashboard/', views.client_dashboard, name='dashboard'),
]
