# Sistema/backend/core/middleware.py

import traceback
from .models import ErrorLog
from django.utils.deprecation import MiddlewareMixin

import time
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

from django.contrib.auth import get_user_model

User = get_user_model()

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

class AnoLetivoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ano_id = request.GET.get('ano')
        if ano_id:
            request.session['ano_selecionado'] = int(ano_id)
        return self.get_response(request)

class InactivityLogoutMiddleware:
    """
    Desloga usuários após um período de inatividade.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Só para usuários autenticados
        if hasattr(request, 'user') and request.user.is_authenticated:
            now = time.time()
            last = request.session.get('last_activity', now)

            # Pega o tempo máximo de inatividade (em segundos)  
            max_age = getattr(settings, 'SESSION_COOKIE_AGE', None)
            # Fallback caso não exista (aqui usamos 45 minutos)
            if max_age is None:
                max_age = 60 * 45

            # Se passou do limite configurado //~ ou 5min (modo teste)
            if now - last > max_age or now - last > (60 * 45):
                logout(request)
                messages.info(request, "Você foi desconectado por inatividade.")
                return redirect('accounts:login')

            # Atualiza tempo de última atividade
            request.session['last_activity'] = now

        return self.get_response(request)
    