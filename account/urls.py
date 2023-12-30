from django.urls import path
from .views import AccountLoginView, AccountRegisterView


urlpatterns = [
    path('', AccountLoginView.as_view(), name='account_login'),
    path('register/', AccountRegisterView.as_view(), name='account_register'),
]