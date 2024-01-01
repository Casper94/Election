from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', VoterDashboardView.as_view(), name='voterDashboard'),
    path('ballot/vote', ShowBallotView.as_view(), name='show_ballot'),
    path('ballot/vote/preview', PreviewVoteView.as_view(), name='preview_vote'),
    path('ballot/vote/submit', SubmitBallotView.as_view(), name='submit_ballot'),

]