from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),
    path("settings", views.settings_view, name="settings"),
    path("tasks", views.tasks_view, name="tasks"),
    path("invite/<str:token>", views.accept_invitation, name="accept_invitation"),
    
    # Project and Task URLs
    path("project/<int:project_id>/tasks", views.project_tasks, name="project_tasks"),
    path("project/<int:project_id>/create-task", views.create_task, name="create_task"),
    path("task/<int:task_id>", views.task_detail, name="task_detail"),
    path("task/<int:task_id>/edit", views.edit_task, name="edit_task"),
    path("task/<int:task_id>/delete", views.delete_task, name="delete_task"),
    path("task/<int:task_id>/status", views.update_task_status, name="update_task_status"),
    path("task/<int:task_id>/add-subtask", views.add_subtask, name="add_subtask"),
    path("subtask/<int:subtask_id>/toggle", views.toggle_subtask, name="toggle_subtask"),
]