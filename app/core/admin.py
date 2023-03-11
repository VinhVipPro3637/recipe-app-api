"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    """Define admin pages for users"""
    ordering = ["id"]
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('emnail', 'password')}),
        (
            _('Permissions'),
            {
                'fields':(
                    'is_active',
                    'is_staff',
                    'is_supperuser',
                )
            }
        ),
        (_('Important date'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_supperuser',
            ),
        }
        ),
    )


admin.site.register(models.User, UserAdmin)