# Generated migration for UserProfile and Notification models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Tasks', '0003_teaminvitation'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.FileField(blank=True, null=True, upload_to='avatars/')),
                ('bio', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('enable_email_notifications', models.BooleanField(default=True)),
                ('enable_telegram_notifications', models.BooleanField(default=False)),
                ('telegram_chat_id', models.CharField(blank=True, max_length=100)),
                ('notify_on_task_assignment', models.BooleanField(default=True)),
                ('notify_on_task_completion', models.BooleanField(default=True)),
                ('notify_on_comment', models.BooleanField(default=True)),
                ('notify_on_team_invitation', models.BooleanField(default=True)),
                ('notify_on_subtask_assignment', models.BooleanField(default=True)),
                ('dark_mode', models.BooleanField(default=False)),
                ('theme_color', models.CharField(choices=[('blue', 'Blue'), ('purple', 'Purple'), ('green', 'Green'), ('red', 'Red'), ('indigo', 'Indigo')], default='blue', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('task_assigned', 'Task Assigned'), ('task_completed', 'Task Completed'), ('comment_added', 'Comment Added'), ('team_invitation', 'Team Invitation'), ('subtask_assigned', 'Subtask Assigned'), ('task_mentioned', 'Task Mentioned')], max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('email_sent', models.BooleanField(default=False)),
                ('telegram_sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('related_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='Tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='Tasks_notif_user_id_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', '-created_at'], name='Tasks_notif_user_id_created_idx'),
        ),
    ]
