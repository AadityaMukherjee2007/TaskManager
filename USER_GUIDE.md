# TaskManager - User Guide & Quick Start

## 🚀 Quick Start

## 📲 Telegram Bot Integration

### Setup
1. Add your Telegram bot token to the `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN="your-bot-token-here"
   ```
2. The Django app will load this token automatically.

### Sending a Telegram Message (Demo)
You can test the integration by visiting:

```
http://localhost:8000/telegram-test-message/?chat_id=YOUR_CHAT_ID
```

Replace `YOUR_CHAT_ID` with your Telegram user or group chat ID.

If successful, you will receive a message from your bot: `Hello from TaskManager Django!`

### Usage in Code
To send a message from your Django logic:

```python
from Tasks.telegram_utils import send_telegram_message
send_telegram_message(chat_id, "Your message here")
```

The function is safe to use in views, signals, or any backend logic.

### Step 1: Setup
```bash
cd /workspaces/TaskManager/TaskManager
pip install django
python manage.py migrate
python manage.py runserver
```

The server will run at `http://localhost:8000`

### Step 2: Register Users
Visit `http://localhost:8000/register` and create at least 2 users:
- **User 1**: Email: `user1@example.com`, Password: `password123`
- **User 2**: Email: `user2@example.com`, Password: `password123`

### Step 3: Create Team & Invite Members
- Login as User 1
- Go to Settings
- Create a team (e.g., "My Project Team")
- Invite User 2 via email: `user2@example.com`

### Step 4: Accept Invitation
- In development, check the console for invitation email
- User 2 logs in and accepts the invitation
- User 2 is now a team member

### Step 5: Create Project & Tasks
- Create a project in the team
- User 1 creates a task and assigns it to User 2
- User 2 can view and manage the assigned task

---

## 📝 Complete User Workflows

### Workflow 1: Team Admin Creates and Assigns Work

**User 1 (Admin)**
```
1. Register → user1@example.com / password123
2. Login
3. Dashboard → Settings
4. Create Team:
   Name: "Development Team"
   Description: "Building the new features"
5. Back to Settings → Click on your team
6. Invite Members:
   - user2@example.com
   - user3@example.com
7. Create Project:
   Name: "Website Redesign"
   Description: "Redesigning company website"
8. Create Task 1:
   Title: "Design Homepage"
   Assign to: User 2
   Priority: High
   Due Date: 2026-02-01
9. Create Task 2:
   Title: "Setup Database"
   Assign to: User 3
   Priority: High
   Due Date: 2026-01-31
```

### Workflow 2: Team Member Accepts Invitation & Works on Task

**User 2 (Team Member)**
```
1. Receives email: "You're invited to join Development Team"
2. Clicks invitation link
3. If not registered yet:
   - Register with email: user2@example.com
4. If registered:
   - Login
   - Click invitation link
   - Accept invitation
5. See "Development Team" in Teams list
6. View "Website Redesign" project
7. View assigned task "Design Homepage"
8. Click task to see details
9. Add comment: "Starting work on homepage design"
10. Update status to "In Progress"
11. Upload design files (if attachment feature used)
12. When done, update status to "Completed"
```

### Workflow 3: Cross-Functional Task Assignment

**User 1**
```
1. Create task: "Code Review for Homepage"
2. Assign to: User 3 (QA Team Lead)
3. Add description: "Please review the homepage design and CSS"
4. Set priority: Medium
5. User 3 receives notification
```

**User 3**
```
1. Accepts team invitation
2. Sees task "Code Review for Homepage"
3. Reviews task details
4. Adds comment: "Looks good, but need to adjust mobile view"
5. Changes status to "In Review"
6. User 1 gets notified to make changes
```

---

## 🎯 Key Features Usage

### Creating a Task for Someone Else

```
1. Go to Project → Create Task
2. Enter task details:
   - Title: Task name
   - Description: Detailed information
   - Priority: low/medium/high/urgent
   - Start Date: When work starts
   - Due Date: When work is due
   - Assign To: Select team member (dropdown)
3. Click "Create Task"
4. Activity log shows: "Assigned task to [username]"
```

### Managing Task Status

```
1. View Task Details
2. Change Status:
   - Click status dropdown
   - Select: To Do / In Progress / In Review / Completed / Cancelled
3. System logs: "Changed status from [old] to [new]"
4. Completed tasks show completion timestamp
```

### Team Invitations

```
As Team Admin:
1. Settings → Managed Teams
2. Click your team name
3. Enter email address
4. Click "Send Invitation"
5. System generates token and sends email

As Invited User:
1. Check email for invitation link
2. Click link (or copy into browser)
3. If not registered: Register first with that email
4. If registered: Login and accept
5. Automatically added to team members
```

### Collaborating on Tasks

```
1. View Task Details
2. Scroll to Comments section
3. Add Comment:
   - Type your message
   - Click "Add Comment"
4. See all comments with author and timestamp
5. Activity log shows: "[User] Added a comment"
```

### Creating Subtasks

```
1. View Task Details
2. Click "Add Subtask"
3. Enter subtask title
4. Assign to team member (optional)
5. Check/uncheck to mark complete
6. Useful for breaking down large tasks
```

---

## 📧 Email Invitation Examples

### Development Environment (Console)

When you invite someone, the email appears in your console:

```
Subject: You're invited to join Development Team on TaskManager

Hello,

john_doe has invited you to join the team "Development Team" on TaskManager.

To accept this invitation, click the link below or copy it into your browser:
http://localhost:8000/invite/ABC123XYZ...

This invitation will expire in 7 days.

If you don't have a TaskManager account yet, you'll need to create one 
before accepting the invitation.

Best regards,
TaskManager Team
```

### Production Environment

Configure SMTP in `settings.py` to send real emails:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🔍 Filtering & Sorting Tasks

### In Project Task View

**Filter By Status:**
- All tasks
- To Do
- In Progress
- In Review
- Completed
- Cancelled

**Filter By Priority:**
- All priorities
- Low
- Medium
- High
- Urgent

**Filter By Assignee:**
- All team members
- Select specific person

**Sort By:**
- Created date (newest first)
- Created date (oldest first)
- Due date (soonest first)
- Due date (latest first)
- Priority

---

## 👥 Multi-User Scenarios

### Scenario: Daily Standup

**Monday Morning:**
1. Manager creates 5 tasks for the week
2. Each task assigned to specific team member
3. Team members see their assignments
4. Each updates status: "In Progress" when starting

**Daily:**
1. Team members comment progress
2. Manager reviews activity log
3. Update status as work progresses
4. Mark complete when finished

**Friday:**
1. All tasks marked "Completed"
2. Activity log shows entire week's work
3. Team gets summary of accomplishments

### Scenario: Code Review Process

1. Developer creates task: "Implement User Login"
2. Assign to: QA Team Lead
3. Developer adds comment: "Ready for review"
4. QA updates status to "In Review"
5. QA adds comment: "Found 2 bugs, see details..."
6. Developer changes status back to "In Progress"
7. Developer fixes bugs
8. Developer changes to "In Review" again
9. QA verifies and marks "Completed"

---

## ⚙️ Settings & Profile Management

### Update Profile
- Go to Settings
- Update First Name, Last Name, Email
- Click "Save Changes"

### Change Password
- Go to Settings
- Enter current password
- Enter new password (8+ characters)
- Confirm new password
- Click "Change Password"

### Manage Teams
- View teams you're a member of
- See teams you admin
- For admin teams: Invite new members by email

---

## 🔐 Security & Privacy

### Your Data is Protected
- Passwords are hashed (never stored in plain text)
- Email invitations use secure tokens
- Tokens expire after 7 days
- Only team members can see projects and tasks
- Access control on all operations

### What Information is Visible
- Team members can see all tasks in team projects
- Only assigned user can modify their tasks
- Team admin can modify any task
- Comments are visible to all team members
- Activity log shows all changes

---

## 📱 Task Status Lifecycle

```
┌─────────┐
│  To Do  │  ← Initial status when task created
└────┬────┘
     │
     ▼
┌──────────────┐
│ In Progress  │  ← Work is being done
└────┬────────┘
     │
     ▼
┌──────────────┐
│  In Review   │  ← Waiting for approval/review
└────┬────────┘
     │
     ├──────────────────┐
     │                  │
     ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  Completed   │   │  Cancelled   │  ← Final states
└──────────────┘   └──────────────┘
```

---

## 🎓 Tips & Best Practices

1. **Use Clear Task Titles**
   - Bad: "Bug fix"
   - Good: "Fix login button not responding on mobile"

2. **Write Detailed Descriptions**
   - Include context, requirements, acceptance criteria
   - Link to related tasks or documentation

3. **Set Realistic Deadlines**
   - Use due dates to set expectations
   - Start date helps track when work should begin

4. **Communicate in Comments**
   - Use comments instead of email for task-related discussion
   - Keeps all information in one place
   - Creates permanent record

5. **Update Status Regularly**
   - Keep task status current
   - Helps team see progress
   - Better for planning and reporting

6. **Use Priorities Effectively**
   - Urgent: Do immediately, blocks other work
   - High: Do this week
   - Medium: Do this month
   - Low: Do when you have time

---

## ❓ Frequently Asked Questions

**Q: Can I reassign a task after creating it?**
A: Yes! Click the task, then click the assignee field to change it.

**Q: What if an invitation email doesn't arrive?**
A: In development, check your console. In production, check spam folder and ensure SMTP is configured.

**Q: Can I delete a task?**
A: Yes, as the task author or team admin. Click the task and select "Delete".

**Q: Can I see what other team members are working on?**
A: Yes! Go to Project Tasks and see all tasks. Filter by assignee to see who's doing what.

**Q: How long do invitations last?**
A: 7 days. After that, the team admin needs to send a new one.

**Q: What if I have the same email in different teams?**
A: You can be a member of multiple teams with one account.

---

## 📞 Need Help?

- Check this guide for common tasks
- Review the FEATURES.md for technical details
- Check console output for error messages
- Ensure email is configured for invitations

---

**Enjoy using TaskManager! 🎉**
