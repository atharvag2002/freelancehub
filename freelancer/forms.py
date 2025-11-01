from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from .models import FreelancerProfile

class FreelancerRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        user.user_type = 'freelancer'
        if commit:
            user.save()
        return user

class FreelancerProfileForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'List your skills (e.g., Python, JavaScript, UI/UX Design)'
        })
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Write a brief description about yourself and your experience'
        })
    )

    class Meta:
        model = FreelancerProfile
        fields = ['skills', 'bio']
