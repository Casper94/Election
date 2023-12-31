from django.urls import path
from .views import AccountLoginView, AccountRegisterView, AccountLogoutView


urlpatterns = [
    path('', AccountLoginView.as_view(), name='account_login'),
    path('register/', AccountRegisterView.as_view(), name='account_register'),
    path('logout/', AccountLogoutView.as_view(), name='account_logout'),

]