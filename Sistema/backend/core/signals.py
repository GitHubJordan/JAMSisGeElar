from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import AccessLog

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print('Signal de login disparado para:', user)
    AccessLog.objects.create(user=user, action='LOGIN')

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # Em logout, user pode ser None se a sessão já expirou
    if user and hasattr(user, 'is_authenticated'):
        AccessLog.objects.create(user=user, action='LOGOUT')
