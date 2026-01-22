from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Team(models.Model):
    """Team model for grouping users and projects"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='teams')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Teams'

    def __str__(self):
        return self.name


class Project(models.Model):
    """Project model for organizing tasks within a team"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('team', 'name')

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task model with team collaboration features"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Timeline
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
        ]

    def __str__(self):
        return self.title

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


class TaskComment(models.Model):
    """Comments on tasks for collaboration"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"


class SubTask(models.Model):
    """Subtasks for breaking down larger tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subtasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title


class TaskAttachment(models.Model):
    """File attachments for tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_attachments/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.task}"


class TaskActivity(models.Model):
    """Activity log for tracking task changes"""
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('commented', 'Commented'),
        ('completed', 'Completed'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activity_log')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Task Activities'

    def __str__(self):
        return f"{self.activity_type} by {self.user}"


class TeamInvitation(models.Model):
    """Model to track team invitations sent via email"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    email = models.EmailField()
    token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_invitations')
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('team', 'email')
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.team}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at and self.status == 'pending'

class UserProfile(models.Model):
    """Extended user profile with notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.FileField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Notification Preferences
    enable_email_notifications = models.BooleanField(default=True)
    enable_telegram_notifications = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    
    # Notification Events
    notify_on_task_assignment = models.BooleanField(default=True)
    notify_on_task_completion = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_team_invitation = models.BooleanField(default=True)
    notify_on_subtask_assignment = models.BooleanField(default=True)
    
    # Display Preferences
    dark_mode = models.BooleanField(default=False)
    theme_color = models.CharField(
        max_length=20,
        choices=[
            ('blue', 'Blue'),
            ('purple', 'Purple'),
            ('green', 'Green'),
            ('red', 'Red'),
            ('indigo', 'Indigo'),
        ],
        default='blue'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class Notification(models.Model):
    """Notification model for tracking user notifications"""
    NOTIFICATION_TYPES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('comment_added', 'Comment Added'),
        ('team_invitation', 'Team Invitation'),
        ('subtask_assigned', 'Subtask Assigned'),
        ('task_mentioned', 'Task Mentioned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    
    email_sent = models.BooleanField(default=False)
    telegram_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"