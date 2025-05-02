from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser, SwapRequest, Notification

@receiver(post_save, sender=SwapRequest)
def create_swaprequest_notification(sender, instance, created, **kwargs):
    """
    Creates a UserActivityLog entry when a new UserProfile is created.
    """
    if created:
        Notification.objects.create(
            user=instance.user,
            message = f"{instance.user.username} you have received a new swap Request"
        )

    else:
        Notification.objects.update(
            user = instance.user,
            message = f"There has been an update on your swap request from {instance.user.username}"
        )