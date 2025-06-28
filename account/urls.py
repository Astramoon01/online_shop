from django.urls import path
from .api.views import LogoutView
from .views import SignupPageView, VerifyPageView, LoginPageView, ConfirmInfoView, AddAddressView

urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup-page'),
    path('verify/', VerifyPageView.as_view(), name='verify-page'),
    path('login/', LoginPageView.as_view(), name='login-page'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('confirm-info/', ConfirmInfoView.as_view(), name='confirm_info'),
    path("add-address/", AddAddressView.as_view(), name="add_address"),

]
