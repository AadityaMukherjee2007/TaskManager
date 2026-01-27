
from django.urls import path
from . import views
from .team_tasks_view import team_tasks

urlpatterns = [
    path("tasks/edit/<int:task_id>/", views.ajax_edit_task, name="ajax_edit_task"),
    path("tasks/reorder/", views.reorder_tasks, name="reorder_tasks"),
    path("team/create", views.create_team, name="create_team"),
    path("", views.dashboard, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),
    path("profile", views.profile_view, name="profile"),
    path("change-password", views.change_password, name="change_password"),
    path("toggle-dark-mode", views.toggle_dark_mode, name="toggle_dark_mode"),
    path("settings", views.settings_view, name="settings"),
    path("tasks", views.tasks_view, name="tasks"),
    path("invite/<str:token>", views.accept_invitation, name="accept_invitation"),
    # Project and Task URLs
    path("project/create/<int:team_id>", views.create_project, name="create_project"),
    path("project/<int:project_id>/tasks", views.project_tasks, name="project_tasks"),
    path("project/<int:project_id>/create-task", views.create_task, name="create_task"),
    path("task/<int:task_id>", views.task_detail, name="task_detail"),
    path("task/<int:task_id>/edit", views.edit_task, name="edit_task"),
    path("task/<int:task_id>/delete", views.delete_task, name="delete_task"),
    # Comment edit/delete
    path("comment/<int:comment_id>/edit", views.edit_comment, name="edit_comment"),
    path("comment/<int:comment_id>/delete", views.delete_comment, name="delete_comment"),
    path("task/<int:task_id>/status", views.update_task_status, name="update_task_status"),
    path("task/<int:task_id>/add-subtask", views.add_subtask, name="add_subtask"),
    path("subtask/<int:subtask_id>/toggle", views.toggle_subtask, name="toggle_subtask"),
    path("team/<int:team_id>/tasks", team_tasks, name="team_tasks"),
    path("team/<int:team_id>/rename", views.rename_team, name="rename_team"),
    path("team/<int:team_id>/delete", views.delete_team, name="delete_team"),
    path("project/<int:project_id>/rename", views.rename_project, name="rename_project"),
    path("project/<int:project_id>/delete", views.delete_project, name="delete_project"),

    # AJAX endpoint for paginated recent activities
    path("activities/page/<int:page>/", views.activities_page, name="activities_page"),

    # Telegram integration test endpoint
    path("telegram-test-message/", views.telegram_test_message, name="telegram_test_message"),
]
