from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class SignupPageView(TemplateView):
    template_name = 'register/signup.html'

class VerifyPageView(TemplateView):
    template_name = 'register/verify.html'

class LoginPageView(TemplateView):
    template_name = 'register/login.html'

class ConfirmInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'register/confirm_info.html'


class AddAddressView(LoginRequiredMixin, TemplateView):
    template_name = "register/add_address.html"

