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
    print("[DEBUG] Task post_save signal fired.")
    assignee = instance.assignee
    print(f"[DEBUG] Assignee: {assignee}")
    if not assignee:
        print("[DEBUG] No assignee, skipping Telegram notification.")
        return
    try:
        profile = assignee.profile
        print(f"[DEBUG] UserProfile found: {profile}")
    except UserProfile.DoesNotExist:
        print("[DEBUG] UserProfile does not exist for assignee.")
        return
    print(f"[DEBUG] enable_telegram_notifications: {profile.enable_telegram_notifications}, telegram_chat_id: {profile.telegram_chat_id}")
    if not profile.enable_telegram_notifications or not profile.telegram_chat_id:
        print("[DEBUG] Telegram notifications not enabled or chat_id missing.")
        return

    # Respect per-event notification toggles
    # Only send if user wants notifications for assignment or completion
    if created:
        if not getattr(profile, 'notify_on_task_assignment', True):
            print("[DEBUG] User has disabled task assignment notifications.")
            return
        message = (
            f"🔔 *New Task Assigned*\n\n"
            f"Hello {assignee.get_full_name() or assignee.username},\n\n"
            f"You have been assigned a new task in TaskManager.\n\n"
            f"*Task:* {instance.title}\n"
            f"*Project:* {instance.project.name if instance.project else 'N/A'}\n"
            f"*Due Date:* {instance.due_date if instance.due_date else 'Not set'}\n\n"
            f"Please review the task details and get started.\n\n"
            f"Thank you for your collaboration!\n"
            f"— TaskManager Team"
        )
    elif instance.status == 'completed':
        if not getattr(profile, 'notify_on_task_completion', True):
            print("[DEBUG] User has disabled task completion notifications.")
            return
        message = (
            f"✅ *Task Completed*\n\n"
            f"The following task has been marked as completed:\n\n"
            f"*Task:* {instance.title}\n"
            f"*Project:* {instance.project.name if instance.project else 'N/A'}\n\n"
            f"Great job!\n"
            f"— TaskManager Team"
        )
    else:
        message = (
            f"✏️ *Task Updated*\n\n"
            f"The following task has been updated:\n\n"
            f"*Task:* {instance.title}\n"
            f"*Project:* {instance.project.name if instance.project else 'N/A'}\n"
            f"*Status:* {instance.get_status_display()}\n"
            f"*Priority:* {instance.get_priority_display()}\n\n"
            f"Please check TaskManager for more details.\n"
            f"— TaskManager Team"
        )
    print(f"[DEBUG] Sending Telegram message: {message}")
    try:
        send_telegram_message(profile.telegram_chat_id, message)
        print("[DEBUG] Telegram message sent successfully.")
    except Exception as e:
        print(f"[DEBUG] Error sending Telegram message: {e}")


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
