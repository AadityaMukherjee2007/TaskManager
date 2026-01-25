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
    # Only allow team members or admin
    if request.user not in team.members.all() and request.user != team.admin:
        return redirect('dashboard')
    # Handle invite by email
    invite_form = TeamInvitationForm()
    if request.method == 'POST' and request.POST.get('action') == 'invite':
        invite_form = TeamInvitationForm(request.POST)
        if invite_form.is_valid():
            email = invite_form.cleaned_data['email']
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
            # Optionally, send email here
            messages.success(request, f"Invitation sent to {email}!")
            invite_form = TeamInvitationForm()  # reset form
        else:
            messages.error(request, "Please enter a valid email address.")

    # Get all tasks for all projects in this team
    projects = team.projects.all()
    tasks = Task.objects.filter(project__in=projects).select_related('project', 'author', 'assignee')

    # Search logic (by title, description, project)
    from django.db.models import Q
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Find matching projects in this team
        matching_projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(project__in=matching_projects)
        )

    # Optional: Filtering by status, priority, assignee
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    assignee_filter = request.GET.get('assignee')
    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    if priority_filter and priority_filter != 'all':
        tasks = tasks.filter(priority=priority_filter)
    if assignee_filter and assignee_filter != 'all':
        tasks = tasks.filter(assignee_id=assignee_filter)

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
