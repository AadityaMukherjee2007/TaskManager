from django import forms
from django.contrib.auth.models import User
from .models import Task, Project, Team, TaskComment, SubTask, TeamInvitation, UserProfile



class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    assignee = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'id': 'assignee'
        })
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'assignee', 'due_date', 'start_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter task title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter task description (optional)',
                'rows': 4
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'priority'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'status'
            }),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assignee to only team members
        if project:
            team_members = project.team.members.all() | User.objects.filter(managed_teams=project.team)
            self.fields['assignee'].queryset = team_members.distinct()
            self.project = project
        
        # Make assignee not required
        self.fields['assignee'].required = False
        self.fields['assignee'].label = 'Assign to (Team Member)'


class TaskCommentForm(forms.ModelForm):
    """Form for adding comments to tasks"""
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Add a comment...',
                'rows': 3
            })
        }


class SubTaskForm(forms.ModelForm):
    """Form for adding subtasks"""
    class Meta:
        model = SubTask
        fields = ['title', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter subtask title',
                'required': True
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }

    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        if task:
            # Filter assigned_to to only team members
            team_members = task.project.team.members.all() | User.objects.filter(managed_teams=task.project.team)
            self.fields['assigned_to'].queryset = team_members.distinct()
        self.fields['assigned_to'].required = False


class TeamInvitationForm(forms.ModelForm):
    """Form for inviting users to a team"""
    class Meta:
        model = TeamInvitation
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter email address',
                'required': True
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if '@' not in email:
            raise forms.ValidationError('Please enter a valid email address.')
        return email


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter project name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input h-32',
                'placeholder': 'Enter project description (optional)',
                'rows': 4
            })
        }

class UserProfileForm(forms.ModelForm):
    remove_avatar = forms.BooleanField(
        required=False,
        label='Remove avatar',
        widget=forms.CheckboxInput(attrs={'class': 'ml-2'})
    )
    """Form for editing user profile"""
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'avatar', 'remove_avatar', 'dark_mode', 'theme_color', 
                  'enable_email_notifications', 'enable_telegram_notifications', 'telegram_chat_id',
                  'notify_on_task_assignment', 'notify_on_task_completion', 
                  'notify_on_comment', 'notify_on_team_invitation', 'notify_on_subtask_assignment']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Phone Number',
                'type': 'tel'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'telegram_chat_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Your Telegram Chat ID (optional)',
                'type': 'text'
            }),
            'dark_mode': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'theme_color': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'enable_email_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'enable_telegram_notifications': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'notify_on_task_assignment': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'notify_on_task_completion': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'notify_on_comment': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'notify_on_team_invitation': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
            'notify_on_subtask_assignment': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500'
            }),
        }