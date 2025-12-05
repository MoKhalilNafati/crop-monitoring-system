from django.apps import AppConfig

class AgentModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent_module'

    def ready(self):
        # This import is CRITICAL. Without it, signals.py never runs.
        import agent_module.signals