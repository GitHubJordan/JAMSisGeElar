# Sistema/backend/core/middleware.py

import traceback
from .models import ErrorLog
from django.utils.deprecation import MiddlewareMixin

class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware que captura exceções não tratadas e grava em ErrorLog.
    """

    def process_exception(self, request, exception):
        # Obtém nome do usuário ou 'Anonymous'
        username = 'Anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            username = request.user.username  # Usamos o username, não o objeto User

        path = request.path
        message = str(exception)
        stack = traceback.format_exc()

        # Cria registro de erro com os campos CORRETOS do modelo
        ErrorLog.objects.create(
            usuario=username,       # Campo correto: 'usuario'
            url=path,               # Campo correto: 'url'
            mensagem_erro=message,  # Campo correto: 'mensagem_erro'
            traceback=stack         # Campo correto: 'traceback'
        )
        return None
    