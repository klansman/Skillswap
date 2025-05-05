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
    else:
        try:
            old_instance = SwapRequest.objects.get(pk=instance.pk)
        except SwapRequest.DoesNotExist:
            old_instance = None

        if old_instance and old_instance.status != instance.status:
            Notification.objects.create(
                sender = instance.sender,
                message = f"{instance.receiver.username} has {instance.status.lower} your swap request"
            )