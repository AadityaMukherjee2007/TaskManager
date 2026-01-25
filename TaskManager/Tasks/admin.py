from django.contrib import admin
from .models import Task, Team, Project, TaskComment, SubTask, TaskAttachment, TaskActivity, TeamInvitation, UserProfile, Notification
# Register your models here.

admin.site.register(Task)
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(TaskComment)
admin.site.register(SubTask)
admin.site.register(TaskAttachment)
admin.site.register(TaskActivity)
admin.site.register(TeamInvitation)
admin.site.register(UserProfile)
admin.site.register(Notification)