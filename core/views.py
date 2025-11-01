from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Project, Proposal, Message
from .forms import ProjectForm, ProposalForm, MessageForm


def index(request):
    return render(request, 'index.html')


@login_required
def project_list(request):
    """List all open projects with search & filtering (accessible to freelancers)"""
    if request.user.user_type == 'freelancer':
        # Freelancers see all open projects with search/filtering
        projects = Project.objects.filter(status='open')
        
        # Search by title or description
        query = request.GET.get('q')
        if query:
            projects = projects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        
        # Filter by minimum budget
        min_budget = request.GET.get('min_budget')
        if min_budget:
            try:
                projects = projects.filter(budget__gte=float(min_budget))
            except ValueError:
                pass
        
        # Filter by maximum budget
        max_budget = request.GET.get('max_budget')
        if max_budget:
            try:
                projects = projects.filter(budget__lte=float(max_budget))
            except ValueError:
                pass
        
        # Sort by
        sort_by = request.GET.get('sort', '-created_at')
        if sort_by in ['-created_at', 'created_at', '-budget', 'budget']:
            projects = projects.order_by(sort_by)
    else:
        # Clients see their own projects
        projects = Project.objects.filter(client=request.user)
    
    context = {
        'projects': projects,
        'query': request.GET.get('q', ''),
        'min_budget': request.GET.get('min_budget', ''),
        'max_budget': request.GET.get('max_budget', ''),
        'sort_by': request.GET.get('sort', '-created_at'),
    }
    return render(request, 'core/project_list.html', context)


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


@login_required
def project_messages(request, project_id):
    """View and send messages for a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Get the accepted proposal to find the freelancer
    accepted_proposal = project.proposals.filter(status='accepted').first()
    
    # Check permissions: Only client who owns project or hired freelancer can access
    can_access = False
    if request.user.user_type == 'client' and project.client == request.user:
        can_access = True
    elif request.user.user_type == 'freelancer' and accepted_proposal and accepted_proposal.freelancer == request.user:
        can_access = True
    
    if not can_access:
        messages.error(request, "You don't have permission to access this conversation.")
        return redirect('core:project_list')
    
    # Only allow messaging on in-progress projects
    if project.status != 'in_progress':
        messages.warning(request, "Messaging is only available for projects in progress.")
        return redirect('core:project_detail', project_id=project_id)
    
    # Handle message submission
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.project = project
            message.sender = request.user
            message.save()
            messages.success(request, "Message sent!")
            return redirect('core:project_messages', project_id=project_id)
    else:
        form = MessageForm()
    
    # Get all messages for this project
    project_messages = project.messages.all()
    
    context = {
        'project': project,
        'messages_list': project_messages,
        'form': form,
        'accepted_proposal': accepted_proposal,
    }
    
    return render(request, 'core/project_messages.html', context)
