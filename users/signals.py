from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import SwapRequest, Notification, Message
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
    def notify():
        # Determine who should receive this notification
        target_user = instance.receiver if created else (
            instance.sender if instance.status == 'countered' else instance.receiver
        )

        # Create appropriate message
        if created:
            message = "New swap request received."
        elif instance.status == 'accepted':
            message = "Your request was accepted."
        elif instance.status == 'rejected':
            message = "Your request was rejected."
        elif instance.status == 'countered':
            message = "You received a counter offer."
        else:
            return  # no notification needed

        # Create notification
        notification = Notification.objects.create(
            recipient=target_user,
            swap_request=instance,
            message=message
        )

        # Broadcast via WebSocket after transaction commits
        channel_layer = get_channel_layer()
        serialized = NotificationSerializer(notification).data

        async_to_sync(channel_layer.group_send)(
            f"user_{target_user.id}",
            {
                'type': 'notify',  # ✅ matches method in consumer.py
                'data': serialized
            }
        )

    transaction.on_commit(notify)

@receiver(post_save, sender=Message)
def notify_receiver_on_message(sender, instance, created, **kwargs):
    def send_message():
        if created:
            Notification.objects.create(
                user=instance.receiver,
                message=f"New message from {instance.sender.username}"
            )
    transaction.on_commit(send_message)