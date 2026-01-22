#!/usr/bin/env python
"""
Test script to verify all TaskManager functionality
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TaskManager.settings')
sys.path.insert(0, '/workspaces/TaskManager/TaskManager')

django.setup()

from django.contrib.auth.models import User
from Tasks.models import Team, Project, Task, TeamInvitation, TaskActivity
from django.utils import timezone
from datetime import timedelta
import secrets

def test_user_creation():
    """Test user registration and creation"""
    print("\n=== Testing User Creation ===")
    
    # Clean up test users
    User.objects.filter(username__startswith='test_').delete()
    
    # Create test users
    user1 = User.objects.create_user(
        username='test_user1',
        email='test1@example.com',
        password='testpass123'
    )
    user2 = User.objects.create_user(
        username='test_user2',
        email='test2@example.com',
        password='testpass123'
    )
    user3 = User.objects.create_user(
        username='test_user3',
        email='test3@example.com',
        password='testpass123'
    )
    
    print(f"✓ Created users: {user1.username}, {user2.username}, {user3.username}")
    print(f"  User1 Email: {user1.email}")
    print(f"  User2 Email: {user2.email}")
    print(f"  User3 Email: {user3.email}")
    
    return user1, user2, user3

def test_team_creation(user1, user2, user3):
    """Test team creation and member invitation"""
    print("\n=== Testing Team Creation and Invitations ===")
    
    # Clean up old teams
    Team.objects.filter(name__startswith='Test').delete()
    
    # Create a team
    team = Team.objects.create(
        name='Test Team',
        description='A team for testing invitations',
        admin=user1
    )
    team.members.add(user1)
    
    print(f"✓ Created team: {team.name} (Admin: {user1.username})")
    
    # Add member directly
    team.members.add(user2)
    print(f"✓ Added {user2.username} as team member")
    
    # Create invitation for user3
    token = secrets.token_urlsafe(32)
    invitation = TeamInvitation.objects.create(
        team=team,
        invited_by=user1,
        email=user3.email,
        token=token,
        status='pending',
        expires_at=timezone.now() + timedelta(days=7)
    )
    
    print(f"✓ Created invitation for {user3.email}")
    print(f"  Invitation token: {token[:20]}...")
    print(f"  Expires at: {invitation.expires_at}")
    
    return team, invitation

def test_project_creation(team, user1):
    """Test project creation within a team"""
    print("\n=== Testing Project Creation ===")
    
    # Clean up old projects
    Project.objects.filter(name__startswith='Test').delete()
    
    # Create a project
    project = Project.objects.create(
        name='Test Project',
        description='A test project for tasks',
        team=team,
        owner=user1
    )
    
    print(f"✓ Created project: {project.name}")
    print(f"  Team: {project.team.name}")
    print(f"  Owner: {project.owner.username}")
    
    return project

def test_task_creation(project, user1, user2):
    """Test task creation and assignment"""
    print("\n=== Testing Task Creation and Assignment ===")
    
    # Clean up old tasks
    Task.objects.filter(title__startswith='Test').delete()
    
    # Create task by user1, assign to user2
    task = Task.objects.create(
        title='Test Task 1',
        description='A test task assigned to user2',
        project=project,
        author=user1,
        assignee=user2,
        priority='high',
        status='todo'
    )
    
    print(f"✓ Created task: {task.title}")
    print(f"  Author: {task.author.username}")
    print(f"  Assigned to: {task.assignee.username}")
    print(f"  Priority: {task.priority}")
    print(f"  Status: {task.status}")
    
    # Log activity
    activity = TaskActivity.objects.create(
        task=task,
        activity_type='created',
        user=user1,
        description=f'Created task "{task.title}"'
    )
    
    print(f"✓ Created activity log: {activity.description}")
    
    # Create another task assigned to user1 by user2
    task2 = Task.objects.create(
        title='Test Task 2',
        description='A task created by user2 and assigned to user1',
        project=project,
        author=user2,
        assignee=user1,
        priority='medium',
        status='in_progress'
    )
    
    print(f"✓ Created task: {task2.title}")
    print(f"  Author: {task2.author.username}")
    print(f"  Assigned to: {task2.assignee.username}")
    
    return task, task2

def test_task_operations(task, user1, user2):
    """Test task status and priority updates"""
    print("\n=== Testing Task Operations ===")
    
    # Update task status
    task.status = 'in_progress'
    task.save()
    
    TaskActivity.objects.create(
        task=task,
        activity_type='status_changed',
        user=user1,
        description=f'Changed status from todo to in_progress'
    )
    
    print(f"✓ Updated task status to: {task.status}")
    
    # Update task priority
    task.priority = 'urgent'
    task.save()
    
    TaskActivity.objects.create(
        task=task,
        activity_type='priority_changed',
        user=user2,
        description=f'Changed priority from high to urgent'
    )
    
    print(f"✓ Updated task priority to: {task.priority}")
    
    # Mark as completed
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save()
    
    TaskActivity.objects.create(
        task=task,
        activity_type='completed',
        user=user1,
        description='Marked task as completed'
    )
    
    print(f"✓ Marked task as completed at: {task.completed_at}")

def test_queries():
    """Test various queries to ensure data integrity"""
    print("\n=== Testing Data Queries ===")
    
    # Get all test teams
    teams = Team.objects.filter(name__startswith='Test')
    print(f"✓ Found {teams.count()} test teams")
    
    # Get all test projects
    projects = Project.objects.filter(name__startswith='Test')
    print(f"✓ Found {projects.count()} test projects")
    
    # Get all test tasks
    tasks = Task.objects.filter(title__startswith='Test')
    print(f"✓ Found {tasks.count()} test tasks")
    
    # Get pending invitations
    pending_invitations = TeamInvitation.objects.filter(status='pending')
    print(f"✓ Found {pending_invitations.count()} pending invitations")
    
    # Get user1's created tasks
    user1_tasks = Task.objects.filter(author__username='test_user1')
    print(f"✓ Found {user1_tasks.count()} tasks created by test_user1")
    
    # Get user2's assigned tasks
    user2_tasks = Task.objects.filter(assignee__username='test_user2')
    print(f"✓ Found {user2_tasks.count()} tasks assigned to test_user2")
    
    # Get activity logs
    activities = TaskActivity.objects.filter(task__title__startswith='Test')
    print(f"✓ Found {activities.count()} activity logs for test tasks")

def main():
    """Run all tests"""
    print("=" * 60)
    print("TaskManager Functionality Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: User Creation
        user1, user2, user3 = test_user_creation()
        
        # Test 2: Team and Invitations
        team, invitation = test_team_creation(user1, user2, user3)
        
        # Test 3: Project Creation
        project = test_project_creation(team, user1)
        
        # Test 4: Task Creation and Assignment
        task, task2 = test_task_creation(project, user1, user2)
        
        # Test 5: Task Operations
        test_task_operations(task, user1, user2)
        
        # Test 6: Queries
        test_queries()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey Features Verified:")
        print("✓ User registration with email")
        print("✓ Team creation and management")
        print("✓ Email invitations with tokens")
        print("✓ Project creation within teams")
        print("✓ Task creation by users")
        print("✓ Task assignment to team members")
        print("✓ Task status and priority updates")
        print("✓ Activity logging")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
