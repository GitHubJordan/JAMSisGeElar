from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    """
    Decorator para views (function-based ou método de class-based view)
    que exige que o usuário esteja autenticado e tenha um role.name
    contido em allowed_roles.
    Se não estiver, levanta PermissionDenied (403).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                # Django por padrão redireciona ao login se usar @login_required
                from django.contrib.auth.decorators import login_required
                return login_required(view_func)(request, *args, **kwargs)
            # Verifica se o role do usuário está nos permitidos
            if user.role.name not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
