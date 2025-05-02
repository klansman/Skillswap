from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser, SwapRequest, Notification

@receiver(post_save, sender=SwapRequest)
def create_swap_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.receiver,
            message=f"{instance.sender.username} sent you a skill swap request.",
            swap_request=instance
        )