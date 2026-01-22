from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
import secrets
from .models import Team, Project, Task, TaskComment, TaskActivity, TeamInvitation, SubTask

# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard with task overview and team info"""
    user = request.user
    
    # Get user's teams
    user_teams = user.teams.all()
    managed_teams = user.managed_teams.all()
    all_teams = (user_teams | managed_teams).distinct()
    
    # Get tasks for user
    assigned_tasks = Task.objects.filter(assignee=user).select_related('project', 'author')
    created_tasks = Task.objects.filter(author=user).select_related('project', 'assignee')
    
    # Task statistics
    my_tasks = assigned_tasks
    in_progress = assigned_tasks.filter(status='in_progress').count()
    completed = assigned_tasks.filter(status='completed').count()
    pending = assigned_tasks.filter(status='todo').count()
    urgent_tasks = assigned_tasks.filter(priority='urgent', status__in=['todo', 'in_progress'])
    
    # Recent activities
    recent_activities = TaskActivity.objects.filter(
        task__project__team__in=all_teams
    ).select_related('user', 'task').order_by('-created_at')[:10]
    
    # Upcoming deadlines
    upcoming_deadlines = Task.objects.filter(
        assignee=user,
        status__in=['todo', 'in_progress'],
        due_date__isnull=False
    ).order_by('due_date')[:5]
    
    context = {
        'teams': all_teams,
        'my_tasks': my_tasks,
        'in_progress': in_progress,
        'completed': completed,
        'pending': pending,
        'urgent_tasks': urgent_tasks,
        'recent_activities': recent_activities,
        'upcoming_deadlines': upcoming_deadlines,
    }
    
    return render(request, "Tasks/dashboard.html", context)

@login_required(login_url='login')
def settings_view(request):
    """User settings page"""
    user = request.user
    user_teams = user.teams.all()
    managed_teams = user.managed_teams.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            return render(request, "Tasks/settings.html", {
                'user': user,
                'user_teams': user_teams,
                'managed_teams': managed_teams,
                'message': 'Profile updated successfully!',
                'message_type': 'success'
            })
        
        elif action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not user.check_password(current_password):
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'Current password is incorrect.',
                    'message_type': 'error'
                })
            
            if new_password != confirm_password:
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'New passwords do not match.',
                    'message_type': 'error'
                })
            
            if len(new_password) < 8:
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'Password must be at least 8 characters long.',
                    'message_type': 'error'
                })
            
            user.set_password(new_password)
            user.save()
            
            return render(request, "Tasks/settings.html", {
                'user': user,
                'user_teams': user_teams,
                'managed_teams': managed_teams,
                'message': 'Password changed successfully!',
                'message_type': 'success'
            })
        
        elif action == 'invite_member':
            team_id = request.POST.get('team_id')
            invite_email = request.POST.get('invite_email', '').strip().lower()
            
            try:
                team = Team.objects.get(id=team_id, admin=user)
            except Team.DoesNotExist:
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'You do not have permission to invite members to this team.',
                    'message_type': 'error'
                })
            
            # Validate email format
            if '@' not in invite_email:
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'Please enter a valid email address.',
                    'message_type': 'error'
                })
            
            # Check if user is already a team member
            if User.objects.filter(email=invite_email, teams=team).exists():
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'This user is already a member of this team.',
                    'message_type': 'error'
                })
            
            # Create or update invitation
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(days=7)  # 7 days expiration
            
            invitation, created = TeamInvitation.objects.update_or_create(
                team=team,
                email=invite_email,
                defaults={
                    'invited_by': user,
                    'token': token,
                    'status': 'pending',
                    'expires_at': expires_at
                }
            )
            
            # Send invitation email
            try:
                invitation_link = request.build_absolute_uri(reverse('accept_invitation', args=[token]))
                subject = f"You're invited to join {team.name} on TaskManager"
                message = f"""
Hello,

{user.username} has invited you to join the team "{team.name}" on TaskManager.

Click the link below to accept the invitation:
{invitation_link}

This invitation will expire in 7 days.

Best regards,
TaskManager Team
                """
                
                send_mail(
                    subject,
                    message,
                    'noreply@taskmanager.com',
                    [invite_email],
                    fail_silently=False,
                )
                
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': f'Invitation sent to {invite_email}!',
                    'message_type': 'success'
                })
            except Exception as e:
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': f'Error sending email: {str(e)}',
                    'message_type': 'error'
                })
    
    context = {
        'user': user,
        'user_teams': user_teams,
        'managed_teams': managed_teams,
    }
    return render(request, "Tasks/settings.html", context)


def tasks_view(request):
    return render(request, "Tasks/tasks.html")


@login_required(login_url='login')
def accept_invitation(request, token):
    """Accept a team invitation via email link"""
    try:
        invitation = TeamInvitation.objects.get(token=token)
        
        # Check if invitation is still valid
        if invitation.is_expired():
            return render(request, 'Tasks/invitation_error.html', {
                'message': 'This invitation has expired. Please ask the team admin to send a new one.'
            })
        
        if invitation.status != 'pending':
            return render(request, 'Tasks/invitation_error.html', {
                'message': f'This invitation has already been {invitation.status}.'
            })
        
        # Check if user email matches
        if request.user.email.lower() != invitation.email.lower():
            return render(request, 'Tasks/invitation_error.html', {
                'message': 'You are not logged in with the email address this invitation was sent to. Please log in with the correct account.'
            })
        
        # Accept the invitation
        invitation.team.members.add(request.user)
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.accepted_by = request.user
        invitation.save()
        
        return render(request, 'Tasks/invitation_success.html', {
            'team': invitation.team,
            'message': f'You have successfully joined {invitation.team.name}!'
        })
    
    except TeamInvitation.DoesNotExist:
        return render(request, 'Tasks/invitation_error.html', {
            'message': 'This invitation link is invalid or has expired.'
        })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("dashboard"))
        else:
            return render(request, "Tasks/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "Tasks/login.html")  

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "Tasks/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, password=password)
            user.save()
        except:
            return render(request, "Tasks/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("dashboard"))
    else:
        return render(request, "Tasks/register.html")


# ============ TASK VIEWS ============

@login_required(login_url='login')
def create_task(request, project_id):
    """Create a new task in a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is member of the team
    if request.user not in project.team.members.all() and request.user != project.team.admin:
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        start_date = request.POST.get('start_date')
        assignee_id = request.POST.get('assignee')
        
        # Validate required fields
        if not title:
            return render(request, 'Tasks/create_task.html', {
                'project': project,
                'error': 'Task title is required.',
                'priorities': Task.PRIORITY_CHOICES,
                'team_members': project.team.members.all()
            })
        
        # Create task
        task = Task.objects.create(
            title=title,
            description=description,
            project=project,
            author=request.user,
            priority=priority,
            due_date=due_date if due_date else None,
            start_date=start_date if start_date else None,
        )
        
        # Assign if assignee provided
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
                if assignee in project.team.members.all() or assignee == project.team.admin:
                    task.assignee = assignee
                    task.save()
            except User.DoesNotExist:
                pass
        
        # Log activity
        TaskActivity.objects.create(
            task=task,
            activity_type='created',
            user=request.user,
            description=f'Created task "{title}"'
        )
        
        return redirect('task_detail', task_id=task.id)
    
    context = {
        'project': project,
        'priorities': Task.PRIORITY_CHOICES,
        'team_members': project.team.members.all()
    }
    return render(request, 'Tasks/create_task.html', context)


@login_required(login_url='login')
def task_detail(request, task_id):
    """View task details with comments and subtasks"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check access
    if request.user not in task.project.team.members.all() and request.user != task.project.team.admin:
        return redirect('dashboard')
    
    # Handle status/priority updates via POST
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Task.STATUS_CHOICES):
                old_status = task.status
                task.status = new_status
                if new_status == 'completed':
                    task.completed_at = timezone.now()
                task.save()
                
                TaskActivity.objects.create(
                    task=task,
                    activity_type='status_changed',
                    user=request.user,
                    description=f'Changed status from {old_status} to {new_status}'
                )
                
                return redirect('task_detail', task_id=task.id)
        
        elif action == 'update_priority':
            new_priority = request.POST.get('priority')
            if new_priority in dict(Task.PRIORITY_CHOICES):
                old_priority = task.priority
                task.priority = new_priority
                task.save()
                
                TaskActivity.objects.create(
                    task=task,
                    activity_type='priority_changed',
                    user=request.user,
                    description=f'Changed priority from {old_priority} to {new_priority}'
                )
                
                return redirect('task_detail', task_id=task.id)
        
        elif action == 'assign_task':
            assignee_id = request.POST.get('assignee')
            if assignee_id:
                try:
                    assignee = User.objects.get(id=assignee_id)
                    if assignee in task.project.team.members.all() or assignee == task.project.team.admin:
                        task.assignee = assignee
                        task.save()
                        
                        TaskActivity.objects.create(
                            task=task,
                            activity_type='assigned',
                            user=request.user,
                            description=f'Assigned task to {assignee.username}'
                        )
                except User.DoesNotExist:
                    pass
                
                return redirect('task_detail', task_id=task.id)
        
        elif action == 'add_comment':
            content = request.POST.get('comment_content', '').strip()
            if content:
                TaskComment.objects.create(
                    task=task,
                    author=request.user,
                    content=content
                )
                
                TaskActivity.objects.create(
                    task=task,
                    activity_type='commented',
                    user=request.user,
                    description=f'Added a comment'
                )
                
                return redirect('task_detail', task_id=task.id)
    
    comments = task.comments.all().select_related('author').order_by('-created_at')
    subtasks = task.subtasks.all()
    activity = task.activity_log.all().select_related('user').order_by('-created_at')
    team_members = task.project.team.members.all()
    
    context = {
        'task': task,
        'comments': comments,
        'subtasks': subtasks,
        'activity': activity,
        'task_statuses': Task.STATUS_CHOICES,
        'task_priorities': Task.PRIORITY_CHOICES,
        'team_members': team_members,
    }
    return render(request, 'Tasks/task_detail.html', context)


@login_required(login_url='login')
def edit_task(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user is author or team admin
    if request.user != task.author and request.user != task.project.team.admin:
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        start_date = request.POST.get('start_date')
        
        if not title:
            context = {
                'task': task,
                'error': 'Task title is required.',
                'priorities': Task.PRIORITY_CHOICES,
            }
            return render(request, 'Tasks/edit_task.html', context)
        
        task.title = title
        task.description = description
        task.priority = priority
        task.due_date = due_date if due_date else None
        task.start_date = start_date if start_date else None
        task.save()
        
        TaskActivity.objects.create(
            task=task,
            activity_type='status_changed',
            user=request.user,
            description='Updated task details'
        )
        
        return redirect('task_detail', task_id=task.id)
    
    context = {
        'task': task,
        'priorities': Task.PRIORITY_CHOICES,
    }
    return render(request, 'Tasks/edit_task.html', context)


@login_required(login_url='login')
def delete_task(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id)
    project = task.project
    
    # Check if user is author or team admin
    if request.user != task.author and request.user != task.project.team.admin:
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        task.delete()
        return redirect('project_tasks', project_id=project.id)
    
    context = {'task': task}
    return render(request, 'Tasks/confirm_delete_task.html', context)


@login_required(login_url='login')
def project_tasks(request, project_id):
    """View all tasks in a project with filtering and sorting"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check access
    if request.user not in project.team.members.all() and request.user != project.team.admin:
        return redirect('dashboard')
    
    # Get all tasks for the project
    tasks = project.tasks.all().select_related('author', 'assignee').prefetch_related('comments')
    
    # Filtering
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
    
    team_members = project.team.members.all()
    
    context = {
        'project': project,
        'tasks': tasks,
        'task_statuses': Task.STATUS_CHOICES,
        'task_priorities': Task.PRIORITY_CHOICES,
        'team_members': team_members,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_assignee': assignee_filter,
        'current_sort': sort_by,
    }
    return render(request, 'Tasks/project_tasks.html', context)


@login_required(login_url='login')
def update_task_status(request, task_id):
    """AJAX endpoint to update task status"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check access
    if request.user not in task.project.team.members.all() and request.user != task.project.team.admin:
        return JsonResponse({'success': False}, status=403)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            old_status = task.status
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            
            TaskActivity.objects.create(
                task=task,
                activity_type='status_changed',
                user=request.user,
                description=f'Changed status from {old_status} to {new_status}'
            )
            
            return JsonResponse({'success': True, 'new_status': new_status})
    
    return JsonResponse({'success': False})


@login_required(login_url='login')
def add_subtask(request, task_id):
    """Add a subtask to a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check access
    if request.user not in task.project.team.members.all() and request.user != task.project.team.admin:
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            SubTask.objects.create(
                task=task,
                title=title
            )
        return redirect('task_detail', task_id=task.id)
    
    return redirect('task_detail', task_id=task.id)


@login_required(login_url='login')
def toggle_subtask(request, subtask_id):
    """Toggle a subtask completion status"""
    from .models import SubTask
    
    subtask = get_object_or_404(SubTask, id=subtask_id)
    task = subtask.task
    
    # Check access
    if request.user not in task.project.team.members.all() and request.user != task.project.team.admin:
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        subtask.is_completed = not subtask.is_completed
        subtask.save()
        return redirect('task_detail', task_id=task.id)
    
    return redirect('task_detail', task_id=task.id)
