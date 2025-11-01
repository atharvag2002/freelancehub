from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Project, Proposal
from .forms import ProjectForm, ProposalForm


def index(request):
    return render(request, 'index.html')


@login_required
def project_list(request):
    """List all open projects (accessible to freelancers)"""
    if request.user.user_type == 'freelancer':
        # Freelancers see all open projects
        projects = Project.objects.filter(status='open')
    else:
        # Clients see their own projects
        projects = Project.objects.filter(client=request.user)
    return render(request, 'core/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    """Create a new project (clients only)"""
    if request.user.user_type != 'client':
        messages.error(request, "Only clients can create projects.")
        return redirect('core:index')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            messages.success(request, "Project created successfully!")
            return redirect('core:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'core/project_create.html', {'form': form})


@login_required
def project_detail(request, project_id):
    """View project details"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    if request.user.user_type == 'client' and project.client != request.user:
        messages.error(request, "You don't have permission to view this project.")
        return redirect('client:dashboard')
    
    # Get proposals for clients
    proposals = None
    user_proposal = None
    if request.user.user_type == 'client' and project.client == request.user:
        proposals = project.proposals.all()
    elif request.user.user_type == 'freelancer':
        try:
            user_proposal = project.proposals.get(freelancer=request.user)
        except Proposal.DoesNotExist:
            user_proposal = None
    
    context = {
        'project': project,
        'proposals': proposals,
        'user_proposal': user_proposal,
        'can_submit_proposal': request.user.user_type == 'freelancer' and project.status == 'open' and user_proposal is None,
    }
    
    return render(request, 'core/project_detail.html', context)


@login_required
def project_proposals(request, project_id):
    """View all proposals for a project (clients only)"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.user.user_type != 'client' or project.client != request.user:
        messages.error(request, "You don't have permission to view these proposals.")
        return redirect('client:dashboard')
    
    proposals = project.proposals.all()
    return render(request, 'core/project_proposals.html', {
        'project': project,
        'proposals': proposals,
    })


@login_required
def proposal_create(request, project_id):
    """Submit a proposal for a project (freelancers only)"""
    if request.user.user_type != 'freelancer':
        messages.error(request, "Only freelancers can submit proposals.")
        return redirect('core:index')
    
    project = get_object_or_404(Project, id=project_id)
    
    # Check if project is open
    if project.status != 'open':
        messages.error(request, "This project is no longer accepting proposals.")
        return redirect('core:project_detail', project_id=project_id)
    
    # Check if user already submitted a proposal
    if Proposal.objects.filter(project=project, freelancer=request.user).exists():
        messages.warning(request, "You have already submitted a proposal for this project.")
        return redirect('core:project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.project = project
            proposal.freelancer = request.user
            proposal.save()
            messages.success(request, "Proposal submitted successfully!")
            return redirect('core:project_detail', project_id=project_id)
    else:
        form = ProposalForm()
    
    return render(request, 'core/proposal_create.html', {
        'form': form,
        'project': project,
    })


@login_required
def proposal_list(request):
    """List user's proposals (freelancers)"""
    if request.user.user_type != 'freelancer':
        messages.error(request, "Only freelancers can view their proposals.")
        return redirect('core:index')
    
    proposals = Proposal.objects.filter(freelancer=request.user)
    return render(request, 'core/proposal_list.html', {'proposals': proposals})


@login_required
def proposal_accept(request, proposal_id):
    """Accept a proposal (clients only)"""
    proposal = get_object_or_404(Proposal, id=proposal_id)
    
    if request.user.user_type != 'client' or proposal.project.client != request.user:
        messages.error(request, "You don't have permission to accept this proposal.")
        return redirect('client:dashboard')
    
    if proposal.status != 'pending':
        messages.warning(request, "This proposal has already been processed.")
        return redirect('core:project_proposals', project_id=proposal.project.id)
    
    if request.method == 'POST':
        # Accept the proposal
        proposal.status = 'accepted'
        proposal.save()
        
        # Reject all other proposals for this project
        Proposal.objects.filter(project=proposal.project, status='pending').exclude(id=proposal.id).update(status='rejected')
        
        # Change project status to in_progress
        proposal.project.status = 'in_progress'
        proposal.project.save()
        
        messages.success(request, f"Proposal accepted! Project status updated to 'In Progress'.")
        return redirect('core:project_proposals', project_id=proposal.project.id)
    
    return render(request, 'core/proposal_accept.html', {'proposal': proposal})
