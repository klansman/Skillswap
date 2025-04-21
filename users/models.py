from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)