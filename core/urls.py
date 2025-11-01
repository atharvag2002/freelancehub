from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/proposals/', views.project_proposals, name='project_proposals'),
    path('proposals/create/<int:project_id>/', views.proposal_create, name='proposal_create'),
    path('proposals/my/', views.proposal_list, name='proposal_list'),
    path('proposals/<int:proposal_id>/accept/', views.proposal_accept, name='proposal_accept'),
]
