from django.urls import path
from . import views

app_name = 'freelancer'

urlpatterns = [
    path('register/', views.freelancer_register, name='register'),
    path('login/', views.freelancer_login, name='login'),
    path('logout/', views.freelancer_logout, name='logout'),
    path('dashboard/', views.freelancer_dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]