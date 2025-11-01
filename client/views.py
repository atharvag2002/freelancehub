from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ClientRegistrationForm, ClientProfileForm
from django.contrib.auth.forms import AuthenticationForm
from users.models import User
from core.models import Project, Proposal

def client_register(request):
    if request.method == 'POST':
        user_form = ClientRegistrationForm(request.POST)
        profile_form = ClientProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.user_type = 'client'
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('client:login')
    else:
        user_form = ClientRegistrationForm()
        profile_form = ClientProfileForm()
    return render(request, 'client/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def client_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.user_type == 'client':
                login(request, user)
                return redirect('client:dashboard')
            else:
                # Invalid login for a client
                form.add_error(None, "Please enter a correct username and password for a client account.")
    else:
        form = AuthenticationForm()
    return render(request, 'client/login.html', {'form': form})

@login_required
def client_dashboard(request):
    # Ensure user is a client
    if request.user.user_type != 'client':
        return redirect('core:index')
    
    # Get client's profile
    try:
        profile = request.user.clientprofile
    except:
        profile = None
    
    # Get dashboard stats
    active_projects = Project.objects.filter(client=request.user, status='in_progress')
    completed_projects = Project.objects.filter(client=request.user, status='completed')
    pending_proposals = Proposal.objects.filter(project__client=request.user, status='pending')
    
    # Recent proposals (latest 5)
    recent_proposals = Proposal.objects.filter(project__client=request.user, status='pending').order_by('-created_at')[:5]
    
    # Active projects for display (latest 3)
    active_projects_display = active_projects.order_by('-created_at')[:3]
    
    # Calculate total spent (from completed projects and in-progress projects with accepted proposals)
    total_spent = 0
    for project in Project.objects.filter(client=request.user):
        if project.status == 'completed':
            accepted_proposal = project.proposals.filter(status='accepted').first()
            if accepted_proposal:
                total_spent += accepted_proposal.bid_amount
        elif project.status == 'in_progress':
            accepted_proposal = project.proposals.filter(status='accepted').first()
            if accepted_proposal:
                total_spent += accepted_proposal.bid_amount
    
    context = {
        'profile': profile,
        'active_projects_count': active_projects.count(),
        'completed_projects_count': completed_projects.count(),
        'pending_proposals_count': pending_proposals.count(),
        'hired_freelancers_count': Project.objects.filter(client=request.user, status='in_progress').count(),
        'total_spent': total_spent,
        'recent_proposals': recent_proposals,
        'active_projects': active_projects_display,
    }
    
    return render(request, 'client/dashboard.html', context)

def client_logout(request):
    logout(request)
    return redirect('core:index')
