from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Team, Task, Project

@login_required(login_url='login')
def team_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    # Only allow team members or admin
    if request.user not in team.members.all() and request.user != team.admin:
        return redirect('dashboard')
    # Get all tasks for all projects in this team
    projects = team.projects.all()
    tasks = Task.objects.filter(project__in=projects).select_related('project', 'author', 'assignee')
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
    }
    return render(request, 'Tasks/team_tasks.html', context)
