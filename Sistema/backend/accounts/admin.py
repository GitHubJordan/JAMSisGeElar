from django.contrib import admin
from .models import Role, User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_photo')}),
        ('Permissões', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
