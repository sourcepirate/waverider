from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{{ cookiecutter.project_slug }}.accounts' # Use full path for clarity
    label = 'accounts' # Optional shorter label 