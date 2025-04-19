from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# If you don't need to customize the User admin,
# Django automatically registers the default User admin.
# You can leave this file empty or remove it if default is fine.

# Example of unregistering and re-registering if you needed customization:
# admin.site.unregister(User)
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     # Add customizations here
#     pass 