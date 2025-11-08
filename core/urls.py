from django.urls import path
from . import views, api_views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.project_list, name='project_list'),
    path('find-work/', views.freelancer_find_work, name='freelancer_find_work'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/proposals/', views.project_proposals, name='project_proposals'),
    path('projects/<int:project_id>/messages/', views.project_messages, name='project_messages'),
    path('proposals/create/<int:project_id>/', views.proposal_create, name='proposal_create'),
    path('proposals/client/', views.proposal_list_client, name='proposal_list_client'),
    path('proposals/my/', views.proposal_list, name='proposal_list'),
    path('proposals/<int:proposal_id>/accept/', views.proposal_accept, name='proposal_accept'),
    path('messages/', views.all_messages, name='all_messages'),
    path('freelancers/', views.browse_freelancers, name='browse_freelancers'),
    
    # API endpoints for messaging
    path('api/messages/<int:project_id>/', api_views.get_messages, name='api_get_messages'),
    path('api/messages/<int:project_id>/send/', api_views.send_message, name='api_send_message'),
    path('api/messages/<int:project_id>/new/', api_views.get_new_messages, name='api_get_new_messages'),
]
