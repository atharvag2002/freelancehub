from django.contrib import admin
from .models import Project, Proposal, Message


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


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'project', 'created_at', 'has_attachment']
    list_filter = ['created_at']
    search_fields = ['sender__username', 'project__title', 'content']
    readonly_fields = ['created_at']
    
    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
