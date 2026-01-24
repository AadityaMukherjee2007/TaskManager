from .forms import TaskForm, TaskCommentForm, SubTaskForm, TeamInvitationForm, ProjectForm, UserProfileForm
# --- Create Team View ---
from django.contrib import messages


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
from .models import Team, Project, Task, TaskComment, TaskActivity, TeamInvitation, SubTask, UserProfile, Notification
from .forms import TaskForm, TaskCommentForm, SubTaskForm, TeamInvitationForm, ProjectForm, UserProfileForm

# Create your views here.

@login_required(login_url='login')
def create_team(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Team name is required.')
        else:
            team = Team.objects.create(name=name, description=description, admin=request.user)
            team.members.add(request.user)
            messages.success(request, f'Team "{name}" created successfully!')
            return redirect('dashboard')
    return render(request, 'Tasks/create_team.html')

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
    search_query = request.GET.get('search', '').strip()
    if search_query:
        my_tasks = assigned_tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        # Also search projects
        matching_projects = Project.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query),
            team__in=all_teams
        )
        # Show recent tasks matching search or from matching projects
        recent_tasks = Task.objects.filter(
            Q(assignee=user) | Q(author=user),
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(project__in=matching_projects)
        ).order_by('-created_at')[:10]
    else:
        my_tasks = assigned_tasks
        recent_tasks = Task.objects.filter(
            Q(assignee=user) | Q(author=user)
        ).order_by('-created_at')[:10]
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
        'search_query': search_query,
        'recent_tasks': recent_tasks,
        'user_projects': Project.objects.filter(team__in=all_teams),
    }
    return render(request, "Tasks/dashboard.html", context)

@login_required(login_url='login')
def profile_view(request):
    """User profile page with notification preferences"""
    user = request.user
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get recent activity
    recent_activities = TaskActivity.objects.filter(user=user).order_by('-created_at')[:10]
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save form data
            profile = form.save(commit=False)
            # Update user fields
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.email = form.cleaned_data.get('email', '')
            user.save()
            # Handle avatar removal
            if form.cleaned_data.get('remove_avatar'):
                if profile.avatar:
                    profile.avatar.delete(save=False)
                profile.avatar = None
            profile.user = user
            profile.save()
            from django.contrib import messages
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        # Initialize form with user data
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)
    
    context = {
        'form': form,
        'profile': profile,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'Tasks/profile.html', context)

@login_required(login_url='login')
def toggle_dark_mode(request):
    """Toggle dark mode for the user"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        dark_mode = data.get('dark_mode', False)
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.dark_mode = dark_mode
        profile.save()
        
        return JsonResponse({'status': 'success', 'dark_mode': dark_mode})
    
    return JsonResponse({'status': 'error'}, status=400)

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
            if User.objects.filter(email=invite_email, teams=team).exists() or User.objects.filter(email=invite_email, managed_teams=team).exists():
                return render(request, "Tasks/settings.html", {
                    'user': user,
                    'user_teams': user_teams,
                    'managed_teams': managed_teams,
                    'message': 'This user is already a member of this team.',
                    'message_type': 'error'
                })
            
            # Remove restriction: allow sending multiple invites
            # Optionally, expire previous pending invitations
            TeamInvitation.objects.filter(
                team=team,
                email=invite_email,
                status='pending'
            ).update(status='expired')
            
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
                subject = f"You're invited to join {team.name} on TaskManager!"
                message = f"""
Hi,

{user.get_full_name() or user.username} has invited you to join the team "{team.name}" on TaskManager.

To accept your invitation, please click the link below:
{invitation_link}

This invitation is valid for 7 days.

If you don't have a TaskManager account yet, you can create one before accepting the invite.

We're excited to have you join the team and collaborate on projects and tasks!

If you have any questions, feel free to reply to this email.

Best regards,
The TaskManager Team
                """
                
                from django.conf import settings
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
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
    
    all_teams = (user_teams | managed_teams).distinct()
    user_projects = Project.objects.filter(team__in=all_teams)
    context = {
        'user': user,
        'user_teams': user_teams,
        'managed_teams': managed_teams,
        'teams': all_teams,
        'user_projects': user_projects,
    }
    return render(request, "Tasks/settings.html", context)


@login_required(login_url='login')
def tasks_view(request):
    """View all tasks for the current user across all teams/projects"""
    user = request.user
    
    # Get user's teams
    user_teams = user.teams.all() | user.managed_teams.all()
    user_teams = user_teams.distinct()
    
    # Get all tasks assigned to user or created by user
    assigned_tasks = Task.objects.filter(assignee=user).select_related('project', 'author')
    created_tasks = Task.objects.filter(author=user).select_related('project', 'assignee')
    
    # Combine and deduplicate
    all_tasks = (assigned_tasks | created_tasks).distinct().select_related('project', 'author', 'assignee')
    
    # Filtering
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    project_filter = request.GET.get('project')
    task_type_filter = request.GET.get('type', 'all')  # 'assigned', 'created', 'all'
    
    if task_type_filter == 'assigned':
        tasks = assigned_tasks
    elif task_type_filter == 'created':
        tasks = created_tasks
    else:
        tasks = all_tasks
    
    if status_filter and status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    
    if priority_filter and priority_filter != 'all':
        tasks = tasks.filter(priority=priority_filter)
    
    if project_filter and project_filter != 'all':
        tasks = tasks.filter(project_id=project_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-due_date', 'due_date', '-priority', 'priority']
    if sort_by in valid_sorts:
        tasks = tasks.order_by(sort_by)
    
    # Get user's projects for filter dropdown
    user_projects = Project.objects.filter(
        team__in=user_teams
    ).distinct().order_by('name')
    
    # Statistics
    total_tasks = all_tasks.count()
    assigned_count = assigned_tasks.count()
    created_count = created_tasks.count()
    pending_count = all_tasks.filter(status='todo').count()
    in_progress_count = all_tasks.filter(status='in_progress').count()
    completed_count = all_tasks.filter(status='completed').count()
    urgent_count = all_tasks.filter(priority='urgent', status__in=['todo', 'in_progress']).count()
    
    from datetime import date
    context = {
        'user': user,
        'user_teams': user_teams,
        'assigned_tasks': assigned_tasks,
        'created_tasks': created_tasks,
        'all_tasks': all_tasks,
        'tasks': tasks,
        'user_projects': user_projects,
        'teams': user_teams,
        'total_tasks': total_tasks,
        'assigned_count': assigned_count,
        'created_count': created_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'urgent_count': urgent_count,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'project_filter': project_filter,
        'task_type_filter': task_type_filter,
        'sort_by': sort_by,
    }
    return render(request, "Tasks/tasks.html", context)
def accept_invitation(request, token):
    """Accept a team invitation via email link"""
    try:
        invitation = TeamInvitation.objects.get(token=token)

        # Check if invitation is still valid
        if invitation.is_expired():
            return render(request, 'Tasks/invitation_error.html', {
                'message': 'This invitation has expired. Please ask the team admin to send a new one.'
            })

        # Check if already a member
        if request.user in invitation.team.members.all():
            return render(request, 'Tasks/invitation_success.html', {
                'team': invitation.team,
                'message': f'You are already a member of {invitation.team.name}!'
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
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirmation = request.POST.get("confirmation") or request.POST.get("confirm_password", "")
        
        # Validate inputs
        if not username:
            return render(request, "Tasks/register.html", {
                "message": "Username is required."
            })
        
        if not email or '@' not in email:
            return render(request, "Tasks/register.html", {
                "message": "Valid email address is required."
            })
        
        if password != confirmation:
            return render(request, "Tasks/register.html", {
                "message": "Passwords must match."
            })
        
        if len(password) < 8:
            return render(request, "Tasks/register.html", {
                "message": "Password must be at least 8 characters long."
            })
        
        try:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return render(request, "Tasks/register.html", {
                    "message": "Email address already in use."
                })
            
            user = User.objects.create_user(username, email=email, password=password)
            user.save()
        except Exception as e:
            return render(request, "Tasks/register.html", {
                "message": "Username already taken or other error occurred."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("dashboard"))
    else:
        return render(request, "Tasks/register.html")


# ============ PROJECT VIEWS ============

@login_required(login_url='login')
def create_project(request, team_id):
    """Create a new project in a team"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is admin of the team
    if request.user != team.admin:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.team = team
            project.owner = request.user
            project.save()
            
            return redirect('project_tasks', project_id=project.id)
    else:
        form = ProjectForm()
    
    context = {
        'team': team,
        'form': form,
    }
    return render(request, 'Tasks/create_project.html', context)


# ============ TASK VIEWS ============

@login_required(login_url='login')
def create_task(request, project_id):
    """Create a new task in a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is member of the team
    if request.user not in project.team.members.all() and request.user != project.team.admin:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.author = request.user
            task.save()
            
            # Log activity
            TaskActivity.objects.create(
                task=task,
                activity_type='created',
                user=request.user,
                description=f'Created task "{task.title}"'
            )
            
            # Log assignment activity and send notifications if task was assigned
            if task.assignee:
                TaskActivity.objects.create(
                    task=task,
                    activity_type='assigned',
                    user=request.user,
                    description=f'Assigned task to {task.assignee.username}'
                )
                # Send notification to assignee
                send_notification(
                    user=task.assignee,
                    notification_type='task_assigned',
                    title=f'New Task Assigned: {task.title}',
                    message=f'You have been assigned a new task "{task.title}" in project "{project.name}".',
                    task=task
                )
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(project=project)
    
    context = {
        'project': project,
        'form': form,
        'team_members': project.team.members.all() | User.objects.filter(managed_teams=project.team),
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
                        old_assignee = task.assignee
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
            comment_form = TaskCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()
                
                TaskActivity.objects.create(
                    task=task,
                    activity_type='commented',
                    user=request.user,
                    description=f'Added a comment'
                )
                
                return redirect('task_detail', task_id=task.id)
        
        elif action == 'add_subtask':
            subtask_form = SubTaskForm(request.POST, task=task)
            if subtask_form.is_valid():
                subtask = subtask_form.save(commit=False)
                subtask.task = task
                subtask.save()
                
                return redirect('task_detail', task_id=task.id)
    
    comments = task.comments.all().select_related('author').order_by('-created_at')
    subtasks = task.subtasks.all()
    activity = task.activity_log.all().select_related('user').order_by('-created_at')
    team_members = task.project.team.members.all() | User.objects.filter(managed_teams=task.project.team)
    
    comment_form = TaskCommentForm()
    subtask_form = SubTaskForm(task=task)
    
    context = {
        'task': task,
        'comments': comments,
        'subtasks': subtasks,
        'activity': activity,
        'task_statuses': Task.STATUS_CHOICES,
        'task_priorities': Task.PRIORITY_CHOICES,
        'team_members': team_members,
        'comment_form': comment_form,
        'subtask_form': subtask_form,
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
        form = TaskForm(request.POST, instance=task, project=task.project)
        if form.is_valid():
            task = form.save()
            
            TaskActivity.objects.create(
                task=task,
                activity_type='status_changed',
                user=request.user,
                description='Updated task details'
            )
            
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, project=task.project)
    
    context = {
        'task': task,
        'form': form,
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

@login_required(login_url='login')
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        from django.contrib import messages
        user = request.user
        
        # Verify old password
        if not user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('login')
    
    return render(request, 'Tasks/change_password.html')



from .telegram_utils import send_telegram_message

def send_telegram_notification(chat_id, title, message):
    """Send a Telegram message to the given chat_id with a formatted message."""
    full_message = f"\u2B06\uFE0F *TaskManager Notification* \u2B06\uFE0F\n\n*{title}*\n{message}"
    try:
        send_telegram_message(chat_id, full_message)
    except Exception as e:
        # Optionally log the error
        pass

def send_notification(user, notification_type, title, message, task=None):
    """Send notification via email and/or Telegram"""
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Create notification record
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_task=task
    )
    
    # Send email notification
    if profile.enable_email_notifications:
        send_email_notification(user, title, message)
        notification.email_sent = True
    
    # Send Telegram notification
    if profile.enable_telegram_notifications and profile.telegram_chat_id:
        send_telegram_notification(profile.telegram_chat_id, title, message)
        notification.telegram_sent = True
    
    notification.save()
    return notification


def send_email_notification(user, subject, message):
    """Send email notification to user"""
    try:
        email_body = f"""
Hello {user.first_name or user.username},

{message}

---
TaskManager
"""
        send_mail(
            subject=f'[TaskManager] {subject}',
            message=email_body,
            from_email='noreply@taskmanager.local',
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


def send_telegram_notification(chat_id, subject, message):
    """Send Telegram notification to user"""
    try:
        import requests
        
        # Replace with your actual Telegram bot token
        TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
        
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
            return False
        
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        
        notification_text = f"""
🔔 *TaskManager Notification*

*{subject}*

{message}
"""
        
        data = {
            'chat_id': chat_id,
            'text': notification_text,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False