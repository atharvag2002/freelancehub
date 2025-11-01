from django import forms
from .models import Project, Proposal


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'budget']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your project...'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget amount', 'step': '0.01', 'min': '0.01'}),
        }
        labels = {
            'title': 'Project Title',
            'description': 'Description',
            'budget': 'Budget',
        }


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['cover_letter', 'bid_amount']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Write your proposal cover letter...'}),
            'bid_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your bid amount', 'step': '0.01', 'min': '0.01'}),
        }
        labels = {
            'cover_letter': 'Cover Letter',
            'bid_amount': 'Bid Amount',
        }

