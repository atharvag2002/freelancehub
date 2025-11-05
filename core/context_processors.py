from core.models import Project, Proposal, Review

def freelancer_sidebar(request):
    """Context processor to add freelancer sidebar data to all templates"""
    context = {
        'active_projects_count': 0,
        'pending_proposals_count': 0,
        'completed_projects_count': 0,
        'avg_rating': 0,
        'review_count': 0,
    }
    
    if request.user.is_authenticated and request.user.user_type == 'freelancer':
        try:
            profile = request.user.freelancerprofile
            context.update({
                'profile': profile,
                'avg_rating': profile.avg_rating,
                'review_count': profile.review_count,
            })
        except:
            profile = None
        
        # Get dashboard stats
        active_jobs = Proposal.objects.filter(freelancer=request.user, status='accepted')
        pending_proposals = Proposal.objects.filter(freelancer=request.user, status='pending')
        completed_jobs = Proposal.objects.filter(freelancer=request.user, project__status='completed', status='accepted')
        
        context.update({
            'active_projects_count': active_jobs.count(),
            'pending_proposals_count': pending_proposals.count(),
            'completed_projects_count': completed_jobs.count(),
        })
    
    return context