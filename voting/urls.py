from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dashboard/', VoterDashboardView.as_view(), name='voterDashboard'),
    path('ballot/fetch/', FetchBallotView.as_view(), name='fetch_ballot'),
    path('ballot/vote', ShowBallotView.as_view(), name='show_ballot'),
    path('ballot/vote/preview', PreviewVoteView.as_view(), name='preview_vote'),
    path('ballot/vote/submit', SubmitBallotView.as_view(), name='submit_ballot'),

]