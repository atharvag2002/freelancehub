from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .forms import FreelancerRegistrationForm, FreelancerProfileForm
from django.contrib.auth.forms import AuthenticationForm
from users.models import User
from core.models import Project, Proposal, Review

def freelancer_register(request):
    if request.method == 'POST':
        user_form = FreelancerRegistrationForm(request.POST)
        profile_form = FreelancerProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # Create and save the user
            user = user_form.save()  # This will handle password hashing
            
            # Create and save the profile
            profile = profile_form.save(commit=False)
            profile.user = user  # Link to user
            profile.save()
            
            # Redirect to login page
            return redirect('freelancer:login')
    else:
        user_form = FreelancerRegistrationForm()
        profile_form = FreelancerProfileForm()
    
    return render(request, 'freelancer/freel-register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def freelancer_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.user_type == 'freelancer':
                login(request, user)
                return redirect('freelancer:dashboard')
            else:
                # Invalid login for a freelancer
                form.add_error(None, "Please enter a correct username and password for a freelancer account.")
    else:
        form = AuthenticationForm()
    return render(request, 'freelancer/freel-login.html', {'form': form})

@login_required
def freelancer_dashboard(request):
    # Only allow freelancers to access this page
    if not request.user.user_type == 'freelancer':
        return redirect('core:index')
    
    # Get freelancer's profile
    try:
        profile = request.user.freelancerprofile
    except:
        profile = None
    
    # Get dashboard stats
    active_jobs = Proposal.objects.filter(freelancer=request.user, status='accepted')
    pending_proposals = Proposal.objects.filter(freelancer=request.user, status='pending')
    completed_jobs = Proposal.objects.filter(freelancer=request.user, project__status='completed', status='accepted')
    
    # Best matches (open projects, limit to 3)
    open_projects = Project.objects.filter(status='open').exclude(
        proposals__freelancer=request.user
    ).order_by('-created_at')[:3]
    
    # Active jobs for display
    active_jobs_display = active_jobs.select_related('project').order_by('-created_at')[:3]
    
    # Calculate total earnings (from completed projects)
    total_earnings = sum(proposal.bid_amount for proposal in completed_jobs)
    
    # Get rating and review count from profile
    avg_rating = profile.avg_rating if profile else 0
    review_count = profile.review_count if profile else 0
    
    context = {
        'user': request.user,
        'profile': profile,
        'active_projects_count': active_jobs.count(),
        'pending_proposals_count': pending_proposals.count(),
        'completed_projects_count': completed_jobs.count(),
        'total_earnings': total_earnings,
        'open_projects': open_projects,
        'active_jobs': active_jobs_display,
        'avg_rating': avg_rating,
        'review_count': review_count,
    }
    return render(request, 'freelancer/freel-dashboard.html', context)

def freelancer_logout(request):
    logout(request)
    return redirect('core:index')