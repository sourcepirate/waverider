"""
URL configuration for {{ cookiecutter.project_name }} project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
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

# Import the accounts API
from ninja import NinjaAPI
from {{ cookiecutter.project_slug }}.accounts.api import router as accounts_router

# Create the main API instance
api = NinjaAPI(
    title="{{ cookiecutter.project_name }} API",
    version="1.0.0",
    description="Complete API for {{ cookiecutter.project_name }} with authentication and OAuth2 support"
)

# Add accounts router with proper prefix
api.add_router("/accounts", accounts_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls, name='api'), # Main API mount point with all endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # SimpleJWT refresh URL
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),     # SimpleJWT verify URL
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