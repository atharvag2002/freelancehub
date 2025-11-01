from django.contrib import admin
from .models import Project, Proposal


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'budget', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'client__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['freelancer', 'project', 'status', 'bid_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['freelancer__username', 'project__title', 'cover_letter']
    readonly_fields = ['created_at', 'updated_at']
