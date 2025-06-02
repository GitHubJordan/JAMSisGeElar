from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import User, Role
from .forms import UserCreateForm, UserEditForm # type: ignore
from .decorators import role_required # type: ignore
from django.utils.decorators import method_decorator


@login_required
def redirect_dashboard(request):
    role_name = request.user.role.name
    if role_name == 'Admin':
        return redirect('dashboard:admin-dashboard')
    elif role_name == 'Diretor':
        return redirect('dashboard:diretor-dashboard')
    elif role_name == 'Pedagogico':
        return redirect('dashboard:pedagogico-dashboard')
    elif role_name == 'Secretaria':
        return redirect('dashboard:secretaria-dashboard')
    else:
        # Usuários sem role válida são deslogados e impedidos de acessar
        from django.contrib.auth import logout
        logout(request)
        return redirect('accounts:login')


# Helper Mixin para checar permissão de Role em Class-Based Views
class RoleRequiredMixin:
    """
    Mixin para CBV que checa se o usuário possui role.name em allowed_roles.
    Deve definir `allowed_roles = ['Admin', 'Diretor']` na view.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            # delega ao mixin padrão do Django
            from django.contrib.auth.mixins import LoginRequiredMixin
            return LoginRequiredMixin.dispatch(self, request, *args, **kwargs)
        if user.role.name not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class UserListView(LoginRequiredMixin, ListView):
    """
    RF-05: Listar Usuários (Admin/Diretor).
    Url: /accounts/users/
    """
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.select_related('role').order_by('username')


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class UserCreateView(LoginRequiredMixin, CreateView):
    """
    RF-03: Criar Usuário (Admin/Diretor).
    Url: /accounts/users/new/
    """
    model = User
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user-list')

    def form_valid(self, form):
        # O `UserCreationForm` já faz hash da senha.
        return super().form_valid(form)


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    RF-04: Editar Usuário (Admin/Diretor).
    Url: /accounts/users/edit/<pk>/
    """
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user-list')

    def dispatch(self, request, *args, **kwargs):
        # Impede editar se tentar alterar o próprio status para inativo?
        # Aqui vamos deixar sem essa verificação; caso quisesse, checamos:
        # if self.get_object() == request.user and 'is_active' in request.POST and request.POST['is_active'] == 'False':
        #     request.user.logout()
        return super().dispatch(request, *args, **kwargs)


@method_decorator(role_required('Admin', 'Diretor'), name='dispatch')
class UserDeleteView(LoginRequiredMixin, DeleteView):
    """
    RF-06: Excluir Usuário (Admin/Diretor).
    Url: /accounts/users/delete/<pk>/
    """
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Não permitir excluir se for o próprio em sessão
        if obj == request.user:
            raise PermissionDenied("Não é possível excluir o usuário em sessão.")
        # Se for o último admin, impedir também (lógica simples para MVP)
        if obj.role.name == 'Admin':
            # Conta quantos Admins ativos existem
            admins_ativos = User.objects.filter(role__name='Admin', is_active=True).count()
            if admins_ativos < 2:
                raise PermissionDenied("Deve existir pelo menos um Admin ativo no sistema.")
        return super().dispatch(request, *args, **kwargs)
