from django.urls import path
from .views import VoterDashboardView

urlpatterns = [
    path('dashboard/', VoterDashboardView.as_view(), name='voterDashboard'),
]