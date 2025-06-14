from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
# Create your models here.

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    # ratings = models.IntegerField(blank=True)
    
    def average_rating(self):
        ratings = Rating.objects.filter(ratee=self)
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return None

    def ratings_count(self):
        return self.rate_received.count()


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
    status =  models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('countered', 'Countered')], default='pending')
    counter_to = models.ForeignKey('self', blank= True, null=True, on_delete=models.CASCADE, related_name='counter_offer')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} wants to swap {self.sender_skill} with {self.receiver_skill} of {self.receiver}"
    
User = get_user_model()
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    swap_request =models.ForeignKey(SwapRequest, on_delete=models.CASCADE, null=False, blank=True)
    swap_type = models.CharField(max_length=50, choices=[('new_request', 'New Request'), ('counter_offer', 'Counter Offer')], blank=True)
    related_swap = models.ForeignKey(SwapRequest, on_delete=models.CASCADE, null=True, blank=True, related_name = "related_swap")
    

    def __str__(self):
        return f"To: {self.recipient.username} | Read: {self.is_read} | {self.message[:30]}..."
    

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    swap_request = models.ForeignKey(SwapRequest, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"From {self.sender} to {self.receiver} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
class Rating(models.Model):
    swap = models.ForeignKey(SwapRequest, on_delete=models.CASCADE, related_name='rated_swap')
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rate_sent')
    ratee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rate_received')
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rating']
    def __str__(self):
        return f"Rating {self.rating} from {self.rater} to {self.ratee} on {self.swap}"
