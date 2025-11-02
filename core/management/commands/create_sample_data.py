from django.core.management.base import BaseCommand
from users.models import User
from core.models import Project
from client.models import ClientProfile
from freelancer.models import FreelancerProfile
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates sample projects, clients, and freelancers for testing'

    def handle(self, *args, **kwargs):
        # Sample data
        technologies = [
            'Python', 'JavaScript', 'React', 'Django', 'Node.js', 'Angular',
            'Vue.js', 'PHP', 'Laravel', 'WordPress', 'HTML/CSS', 'Bootstrap',
            'Java', 'Spring Boot', 'Android', 'iOS', 'Swift', 'Flutter'
        ]

        project_titles = [
            'E-commerce Website Development',
            'Mobile App Development',
            'Website Redesign',
            'Custom CRM System',
            'Portfolio Website',
            'Blog Platform Development',
            'API Integration Project',
            'Social Media Dashboard',
            'Inventory Management System',
            'Online Learning Platform',
            'Real Estate Listing Website',
            'Restaurant Ordering System'
        ]

        # Create sample clients
        for i in range(5):
            try:
                username = f'client{i+1}'
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        password='testpass123',
                        first_name=f'Client{i+1}',
                        last_name=f'Test{i+1}',
                        email=f'client{i+1}@example.com'
                    )
                    ClientProfile.objects.create(
                        user=user,
                        company_name=f'Company {i+1}',
                        bio=f'A sample client company {i+1}'
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created client: {username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating client {i+1}: {str(e)}'))

        # Create sample freelancers
        for i in range(5):
            try:
                username = f'freelancer{i+1}'
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        password='testpass123',
                        first_name=f'Freelancer{i+1}',
                        last_name=f'Test{i+1}',
                        email=f'freelancer{i+1}@example.com'
                    )
                    FreelancerProfile.objects.create(
                        user=user,
                        bio=f'Experienced freelancer with skills in various technologies'
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created freelancer: {username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating freelancer {i+1}: {str(e)}'))

        # Create sample projects
        clients = User.objects.filter(clientprofile__isnull=False)
        
        for i in range(15):
            try:
                # Random data for project
                client = random.choice(clients)
                title = random.choice(project_titles)
                required_skills = random.sample(technologies, k=random.randint(2, 5))
                
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                created_date = timezone.now() - timedelta(days=days_ago)
                
                # Random budget between $500 and $10000
                budget = random.randint(500, 10000)
                
                project = Project.objects.create(
                    client=client,
                    title=f'{title} #{i+1}',
                    description=f'This is a sample project that requires expertise in {", ".join(required_skills)}. '
                              f'The project involves creating a robust solution with modern technologies.',
                    budget=budget,
                    created_at=created_date
                )
                self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating project {i+1}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))