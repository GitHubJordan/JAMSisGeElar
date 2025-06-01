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

    def save_model(self, request, obj, form, change):
        # Se for atribuir role Admin a um usuário novo ou editado:
        if obj.role.name == 'Admin':
            # Verifica se há outro Admin ativo, exceto ele mesmo (no caso de change)
            qs = User.objects.filter(role__name='Admin', is_active=True)
            if change:
                qs = qs.exclude(pk=obj.pk)
            if qs.exists():
                from django.contrib import messages
                messages.error(request, "Já existe um usuário Admin ativo. Só pode haver um Admin.")
                return
        super().save_model(request, obj, form, change)

