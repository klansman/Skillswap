from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import SwapRequest, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import NotificationSerializer

from django.db import transaction

@receiver(post_save, sender=SwapRequest)
def create_notification(sender, instance, created, **kwargs):
    if created:
        def notify():
            if instance.counter_to:
                # Counter-offer notification
                Notification.objects.create(
                    recipient=instance.counter_to.sender,
                    message=f"{instance.sender.username} sent you a counter offer.",
                    # type="counter_offer",
                    swap_request=instance
                )
            else:
                # Regular swap request notification
                Notification.objects.create(
                    recipient=instance.receiver,
                    message=f"{instance.sender.username} sent you a swap request.",
                    # type="swap_request",
                    swap_request=instance
                )
        
        transaction.on_commit(notify)


@receiver(post_save, sender=SwapRequest)
def swap_request_notification(sender, instance, created, **kwargs):
    # Determine who should receive this notification
    target_user = instance.receiver if created else instance.sender if instance.status == 'countered' else instance.receiver

    # Avoid duplicate notifications for the same object and user
    if created:
        Notification.objects.create(user=target_user, swap_request=instance, message="New swap request received.")
    elif instance.status == 'accepted':
        Notification.objects.create(user=target_user, swap_request=instance, message="Your request was accepted.")
    elif instance.status == 'rejected':
        Notification.objects.create(user=target_user, swap_request=instance, message="Your request was rejected.")
    elif instance.status == 'countered':
        Notification.objects.create(user=target_user, swap_request=instance, message="You received a counter offer.")

    # Broadcast via WebSocket
    channel_layer = get_channel_layer()
    notification = Notification.objects.filter(user=target_user).latest('timestamp')
    serialized = NotificationSerializer(notification).data

    async_to_sync(channel_layer.group_send)(
        f"user_{target_user.id}",
        {
            'type': 'notify',
            'data': serialized
        }
    )
