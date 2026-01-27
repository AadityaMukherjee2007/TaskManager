def search_query_context(request):
    return {'search_query': request.GET.get('search', '').strip()}
from .models import Team, Project
from django.contrib.auth.models import AnonymousUser

def sidebar_context(request):
    if not hasattr(request, 'user') or isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
        return {}
    user = request.user
    user_teams = user.teams.all() | user.managed_teams.all()
    user_teams = user_teams.distinct()
    user_projects = Project.objects.filter(team__in=user_teams).distinct().order_by('name')
    return {
        'teams': user_teams,
        'user_projects': user_projects,
    }