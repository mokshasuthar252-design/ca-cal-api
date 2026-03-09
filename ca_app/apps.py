from django.apps import AppConfig


class CaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ca_app'

    def ready(self):
        import ca_app.signals