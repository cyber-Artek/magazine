from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import UserRegisterForm, UserProfileForm, UserLoginForm


class UserRegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # show login tab content on the same screen
        context["login_form"] = UserLoginForm()
        context["register_form"] = context.get("form")
        context["active_tab"] = "register"
        return context


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # show registration tab content on the same screen
        context["login_form"] = context.get("form")
        context["register_form"] = UserRegisterForm()
        context["active_tab"] = "login"
        return context


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class UserProfileView(DetailView):
    template_name = 'users/profile.html'
    model = CustomUser
    context_object_name = 'user_obj'


class UserProfileUpdateView(UpdateView):
    template_name = 'users/profile_edit.html'
    model = CustomUser
    form_class = UserProfileForm
    success_url = reverse_lazy('product-list')
    context_object_name = 'user_obj'

    def get_object(self, queryset=None):
        return self.request.user
