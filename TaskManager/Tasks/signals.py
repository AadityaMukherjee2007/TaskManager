from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Task
from .telegram_utils import send_telegram_message
from django.conf import settings

# Send Telegram notification when a Task is created or updated
from django.db.models.signals import post_save
@receiver(post_save, sender=Task)
def send_task_notification(sender, instance, created, **kwargs):
    assignee = instance.assignee
    if not assignee:
        return
    try:
        profile = assignee.profile
    except UserProfile.DoesNotExist:
        return
    if not profile.enable_telegram_notifications or not profile.telegram_chat_id:
        return
    if created:
        message = f"You have been assigned a new task: {instance.title}"
    else:
        message = f"Task updated: {instance.title} (Status: {instance.status})"
    try:
        send_telegram_message(profile.telegram_chat_id, message)
    except Exception as e:
        # Optionally log the error
        pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
