# TaskManager - Complete Task Management System

A Django-based task management application with team collaboration, email invitations, and comprehensive task tracking.

## ✓ Features Implemented

### User Management
- **User Registration**: Users can register with username, email, and password
- **Email Capture**: Email addresses are collected during registration
- **Password Validation**: Passwords must be at least 8 characters long
- **Profile Management**: Users can update their profile information

### Team Management
- **Team Creation**: Create teams for collaborative work
- **Team Administration**: Team admins can manage members
- **Email-Based Invitations**: Invite users to teams via email
- **Invitation Tokens**: Secure token-based invitation system with 7-day expiration
- **Member Management**: Accept/reject team invitations

### Project Management
- **Project Creation**: Create projects within teams
- **Project Organization**: Organize tasks by projects
- **Access Control**: Only team members can access projects

### Task Management
- **Task Creation**: Users can create tasks in projects
- **Task Assignment**: Assign tasks to any team member
- **Task to Team Members**: Create tasks and immediately assign them to colleagues
- **Task Statuses**: Track task progress (To Do, In Progress, In Review, Completed, Cancelled)
- **Task Priorities**: Set priority levels (Low, Medium, High, Urgent)
- **Task Dates**: Set start and due dates for tasks
- **Task Details**: Add detailed descriptions to tasks

### Task Collaboration
- **Comments**: Add comments to tasks for discussion
- **Subtasks**: Break down tasks into subtasks
- **Activity Logging**: Complete audit trail of all task changes
- **Task Updates**: Update status, priority, and assignee

### Email Configuration
- **Console Backend (Development)**: Emails are printed to console during development
- **SMTP Support (Production)**: Easy configuration for production email services
- **Invitation Emails**: HTML-formatted invitation emails with secure links
- **User Friendly**: Clear instructions in invitation emails

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 6.0+
- Virtual Environment

### Install Dependencies
```bash
cd /workspaces/TaskManager/TaskManager
pip install django
python manage.py migrate
```

### Run the Development Server
```bash
python manage.py runserver
```

### Create a Superuser (Optional)
```bash
python manage.py createsuperuser
```

## 📋 Usage Guide

### 1. Register a New Account
- Go to `/register` 
- Enter username, email, and password
- Minimum password length: 8 characters

### 2. Create a Team
- Navigate to Settings
- Create a new team with a name and description

### 3. Invite Team Members via Email
- In Settings, go to your managed teams
- Enter the email address of the person you want to invite
- An invitation email will be sent to them

### 4. Accept Team Invitation
- The invited user receives an email with a link
- They click the link or are redirected to accept the invitation
- If not registered yet, they need to register first with the same email

### 5. Create a Project
- In a team, create a new project
- Add a name and description

### 6. Create Tasks
- In a project, create new tasks
- Tasks can be created by any team member
- Assign tasks to any other team member when creating

### 7. Manage Tasks
- View all tasks in a project with filtering and sorting
- Update task status as work progresses
- Change task priority as needed
- Assign/reassign tasks to team members
- Add comments for collaboration
- Create subtasks to break down work

## 📧 Email Configuration

### Development (Console Backend)
By default, emails are printed to the console:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (SMTP)
Update `settings.py` for production:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@taskmanager.com'
```

## 📁 Project Structure

```
TaskManager/
├── TaskManager/          # Django project settings
│   ├── settings.py       # Django configuration
│   ├── urls.py          # URL routing
│   ├── asgi.py          # ASGI configuration
│   └── wsgi.py          # WSGI configuration
├── Tasks/               # Main Django app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # App URL routes
│   ├── forms.py         # Django forms
│   ├── admin.py         # Admin interface
│   └── templates/       # HTML templates
└── manage.py            # Django management script
```

## 🗄️ Database Models

### Team
- Team members and projects
- Admin user for management
- Created/updated timestamps

### Project
- Belongs to a team
- Has an owner
- Contains multiple tasks

### Task
- Title, description, priority, status
- Assigned to a user
- Created by a user
- Has due dates and start dates
- Related to a project

### TaskComment
- Comments on tasks
- Author and timestamp
- Helps with task discussion

### SubTask
- Break down tasks
- Can be assigned to team members
- Track completion status

### TeamInvitation
- Email-based invitations
- Unique tokens for security
- Status tracking (pending, accepted, rejected, expired)
- 7-day expiration period

### TaskActivity
- Audit log for all task changes
- Tracks who made changes and when
- Documents all updates

## ✨ Key Features Highlights

### 1. Secure Email Invitations
- Unique tokens prevent unauthorized access
- Expiration dates ensure invitations don't stay valid forever
- Email verification ensures correct user account

### 2. Collaborative Task Management
- Multiple users can work on same projects
- Comments facilitate discussion
- Activity log shows all changes
- Subtasks help organize complex work

### 3. Flexible Task Assignment
- Create tasks for yourself or others
- Reassign tasks as needed
- Only team members can be assigned tasks
- Clear visibility of who owns what

### 4. Complete Activity Tracking
- See who created each task
- Track status changes
- Monitor priority updates
- View all comments and changes
- Know when tasks were completed

## 🔒 Security Features

- **Access Control**: Only team members can view projects and tasks
- **Email Verification**: Invitations use email verification
- **Token Security**: Secure token-based invitation system
- **Admin Controls**: Team admins manage member access
- **Permission Checking**: Views validate user access

## 📝 Testing

A comprehensive test suite is included:

```bash
python test_functionality.py
```

This tests:
- User creation and registration
- Team creation and member management
- Email invitations
- Project creation
- Task creation and assignment
- Task operations (status, priority updates)
- Activity logging

## 🔧 Configuration

### Email Settings
Located in `TaskManager/settings.py`:
- `EMAIL_BACKEND`: Console (dev) or SMTP (production)
- `DEFAULT_FROM_EMAIL`: Sender email address
- SMTP credentials for production use

### Database
SQLite is used by default. For production, update `DATABASES` in settings.py

### Allowed Hosts
Update `ALLOWED_HOSTS` in settings.py for deployment

## 💡 Future Enhancements

Potential improvements:
- Task dependencies and milestones
- Time tracking for tasks
- File attachments to tasks
- Task templates and recurring tasks
- Advanced filtering and search
- Task statistics and reporting
- Notification system
- Mobile app

## 📞 Support

For issues or questions, refer to Django documentation:
- [Django Documentation](https://docs.djangoproject.com/)
- [Django Email Documentation](https://docs.djangoproject.com/en/6.0/topics/email/)

## 📄 License

This project is provided as-is for educational and commercial use.

---

**Status**: ✓ All core features are fully functional and tested.
