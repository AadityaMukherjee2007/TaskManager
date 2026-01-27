from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Team, Task, Project, TeamInvitation
from .forms import TeamInvitationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import secrets

@login_required(login_url='login')
def team_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    invite_form = TeamInvitationForm()
    if request.method == 'POST' and request.POST.get('action') == 'invite':
        invite_form = TeamInvitationForm(request.POST)
        if invite_form.is_valid():
            email = invite_form.cleaned_data['email'].strip().lower()
            # Validate email format
            if '@' not in email:
                messages.error(request, 'Please enter a valid email address.')
            # Check if user is already a team member
            elif team.members.filter(email=email).exists() or team.admin.email == email:
                messages.error(request, 'This user is already a member of this team.')
            else:
                # Expire previous pending invites
                TeamInvitation.objects.filter(team=team, email=email, status='pending').update(status='expired')
                token = secrets.token_urlsafe(32)
                expires_at = timezone.now() + timedelta(days=7)
                invitation, created = TeamInvitation.objects.update_or_create(
                    team=team,
                    email=email,
                    defaults={
                        'invited_by': request.user,
                        'token': token,
                        'status': 'pending',
                        'expires_at': expires_at
                    }
                )
                # Send invitation email
                from django.conf import settings
                from django.core.mail import send_mail
                from django.urls import reverse
                remote_domain = "https://azau7zta3g4a.connect.remote.it"
                invitation_path = reverse('accept_invitation', args=[token])
                invitation_link = f"{remote_domain}{invitation_path}"
                subject = f"You're invited to join {team.name} on TaskManager!"
                message = f"""Hi,

{request.user.get_full_name() or request.user.username} has invited you to join the team \"{team.name}\" on TaskManager.

To accept your invitation, please click the link below:
{invitation_link}

This invitation is valid for 7 days.

If you don't have a TaskManager account yet, you can create one before accepting the invite.

We're excited to have you join the team and collaborate on projects and tasks!

If you have any questions, feel free to reply to this email.

Best regards,
The TaskManager Team
"""
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request, f'Invitation sent to {email}!')
                except Exception as e:
                    messages.error(request, f'Error sending email: {str(e)}')
                invite_form = TeamInvitationForm()  # reset form
        else:
            messages.error(request, "Please enter a valid email address.")

    # Always define projects and tasks for both GET and POST
    projects = Project.objects.filter(team=team)
    tasks = Task.objects.filter(project__in=projects).select_related('project', 'author', 'assignee')

    # Add missing filter variables for context
    from django.db.models import Q
    search_query = request.GET.get('search', '').strip() if request.method == 'GET' else ''
    status_filter = request.GET.get('status') if request.method == 'GET' else None
    priority_filter = request.GET.get('priority') if request.method == 'GET' else None
    assignee_filter = request.GET.get('assignee') if request.method == 'GET' else None
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'created_at', '-due_date', 'due_date', '-priority']:
        tasks = tasks.order_by(sort_by)

    team_members = team.members.all()
    # Add teams and user_projects for sidebar
    all_teams = request.user.teams.all() | request.user.managed_teams.all()
    all_teams = all_teams.distinct()
    user_projects = Project.objects.filter(team__in=all_teams)
    context = {
        'team': team,
        'projects': projects,
        'tasks': tasks,
        'task_statuses': Task.STATUS_CHOICES,
        'task_priorities': Task.PRIORITY_CHOICES,
        'team_members': team_members,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_assignee': assignee_filter,
        'current_sort': sort_by,
        'teams': all_teams,
        'user_projects': user_projects,
        'invite_form': invite_form,
        'search_query': search_query,
    }
    return render(request, 'Tasks/team_tasks.html', context)
