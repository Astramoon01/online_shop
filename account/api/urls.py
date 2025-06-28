from django.urls import path
from .views import SignUpView, VerifyOtpView, LoginView, LogoutView, ConfirmUserInfoView, UserAddressListCreateAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify/', VerifyOtpView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('confirm-info/', ConfirmUserInfoView.as_view(), name='confirm-user-info'),
    path("addresses/", UserAddressListCreateAPIView.as_view(), name="user_addresses"),

]
