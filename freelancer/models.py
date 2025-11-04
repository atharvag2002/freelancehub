from django.db import models
from users.models import User

class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated list of skills")
    bio = models.TextField(blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username
    
    def get_skills_list(self):
        """Returns skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []