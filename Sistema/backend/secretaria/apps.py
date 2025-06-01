from django.apps import AppConfig


class SecretariaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'secretaria'

    def ready(self):
        import secretaria.signals  # garante que os receivers sejam registrados
