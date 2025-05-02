from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
# Create your models here.

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)

class Skill(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skill_offered')
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    optionalmsg =models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"
    
class SwapRequest (models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recieved_requests')
    sender_skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='offering_skill')
    receiver_skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='recieving_skill')
    status =  models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} wants to swap {self.sender_skill} with {self.receiver_skill} of {self.receiver}"
    
class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    swap_request =models.ForeignKey(SwapRequest, on_delete=models.CASCADE)

    def __str__(self):
        return super().__str__()