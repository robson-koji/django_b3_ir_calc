from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'django_b3_ir_calc'

    def ready(self):
        import django_b3_ir_calc.signals
