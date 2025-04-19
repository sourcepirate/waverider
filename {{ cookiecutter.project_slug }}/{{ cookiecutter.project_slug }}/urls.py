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
from ninja import NinjaAPI
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import the accounts API router
from {{ cookiecutter.project_slug }}.accounts.api import router as auth_router

# Initialize Django Ninja API
# You can customize options like versioning, docs_url, etc. here
# See: https://django-ninja.rest-framework.com/tutorial/first-steps/
api = NinjaAPI(
    title="{{ cookiecutter.project_name }} API",
    version="1.0.0",
    description="{{ cookiecutter.project_description }}",
    # csrf=True # Enable CSRF protection if needed (requires session auth)
)

# Example Ninja endpoint (can be moved to app-specific files later)
@api.get("/hello")
def hello(request):
    return {"message": "Hello from Django Ninja!"}

# Mount the authentication router
api.add_router("/auth/", auth_router, tags=["Authentication"])

# You can add other app routers here
# from otherapp.api import router as other_router
# api.add_router("/other/", other_router, tags=["Other App"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls, name='api'), # Give the main API mount point a name
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # SimpleJWT refresh URL (name is conventional)
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),     # SimpleJWT verify URL (name is conventional)
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