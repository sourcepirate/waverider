{% if cookiecutter.api_versioning == 'v1' %}
{% set api_prefix = 'api/v1/' %}
{% else %}
{% set api_prefix = 'api/' %}
{% endif %}
"""
URL configuration for {{ cookiecutter.project_name }} project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from ninja import NinjaAPI
from {{ cookiecutter.project_slug }}.accounts.api import router as accounts_router

api = NinjaAPI(
    title="{{ cookiecutter.project_name }} API",
    version="1.0.0",
    description="Complete API for {{ cookiecutter.project_name }} with authentication{% if cookiecutter.include_oauth2 == 'y' %} and OAuth2 support{% endif %}"
)

api.add_router("/accounts", accounts_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('{{ api_prefix }}', api.urls, name='api'),
    path('{{ api_prefix }}token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('{{ api_prefix }}token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add debug toolbar URLs if installed
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass 