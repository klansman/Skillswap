from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser, SwapRequest, Notification

@receiver(post_save, sender=SwapRequest)
def handle_swap_request_notifications(sender, instance, created, **kwargs):
    if created:
        # Notify the receiver of a new request       
        if instance.counter_to:
            Notification.objects.create(
                recipient = instance.counter_to.sender,
                message = f"You have received a counter offer from {instance.sender.username}"
        )
        else:
            Notification.objects.create(
            recipient=instance.receiver,
            message=f"You have a new skill swap request from {instance.sender.username}.",
            swap_request=instance
        )
    else:
        # Fetch previous instance from DB to compare
        try:
            old_instance = SwapRequest.objects.get(pk=instance.pk)
        except SwapRequest.DoesNotExist:
            old_instance = None

        if old_instance and old_instance.status != instance.status:
            Notification.objects.create(
                recipient=instance.sender,
                message=f"Your skill swap request to {instance.receiver.username} was {instance.status.lower()}."
            )


# @receiver(post_save, sender=SwapRequest)
# def handle_swap_request_counter_notifications(sender, instance, created, **kwargs):
#     if instance.counter_to != None :
#         # Notify receiver about a new request
#         Notification.objects.create(
#             recipient=instance.sender,
#             message=f"You have a new skill swap counter request from {instance.receiver.username}."
#         )
#     else:
#         # Notify sender if the status was updated
#         if 'status' in instance.__dict__:  # Check if status field exists (it always will, but for safety)
#             Notification.objects.create(
#                 recipient=instance.sender,
#                 message=f"Your skill swap request to {instance.sender.username} was {instance.status.lower()}."
#             )
