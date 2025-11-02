from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_http_methods
from .models import Project, Message
from django.utils import timezone

@login_required
def get_messages(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project's messages
    if not (project.client == request.user or project.proposals.filter(freelancer=request.user, status='accepted').exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    messages = project.messages.all()
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender.id,
        'is_sent': msg.sender == request.user,
        'created_at': msg.created_at.strftime('%I:%M %p'),
        'attachment': msg.attachment.url if msg.attachment else None
    } for msg in messages]
    
    # Get the other user's info (if client, show freelancer and vice versa)
    if request.user == project.client:
        other_user = project.proposals.filter(status='accepted').first().freelancer
    else:
        other_user = project.client
        
    other_user_data = {
        'name': other_user.get_full_name() or other_user.username,
        'avatar': other_user.profile_pic.url if hasattr(other_user, 'profile_pic') and other_user.profile_pic else f'https://ui-avatars.com/api/?name={other_user.username}'
    }
    
    return JsonResponse({
        'messages': messages_data,
        'project': {
            'id': project.id,
            'title': project.title
        },
        'other_user': other_user_data
    })

@login_required
@require_http_methods(['POST'])
def send_message(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project's messages
    if not (project.client == request.user or project.proposals.filter(freelancer=request.user, status='accepted').exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    content = request.POST.get('content', '').strip()
    attachment = request.FILES.get('attachment')
    
    if not content and not attachment:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    message = Message.objects.create(
        project=project,
        sender=request.user,
        content=content,
        attachment=attachment
    )
    
    return JsonResponse({
        'id': message.id,
        'content': message.content,
        'sender_id': message.sender.id,
        'is_sent': True,
        'created_at': message.created_at.strftime('%I:%M %p'),
        'attachment': message.attachment.url if message.attachment else None
    })

@login_required
def get_new_messages(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    last_id = request.GET.get('last_id')
    
    # Check if user has access to this project's messages
    if not (project.client == request.user or project.proposals.filter(freelancer=request.user, status='accepted').exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    messages = project.messages.filter(id__gt=last_id) if last_id else project.messages.none()
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender.id,
        'is_sent': msg.sender == request.user,
        'created_at': msg.created_at.strftime('%I:%M %p'),
        'attachment': msg.attachment.url if msg.attachment else None
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})