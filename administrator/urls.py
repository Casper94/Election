from django.urls import path
from .views import *


urlpatterns = [
    path('', AdminDashboardView.as_view(), name="adminDashboard"),

    # * Voters
    path('voters/', VotersView.as_view(), name='adminViewVoters'),

    # * Position
    path('positions/view', ViewPositionsView.as_view(), name='viewPositions'),

    # * Candidate
    path('candidate/', ViewCandidatesView.as_view(), name='viewCandidates'),
    path('candidate/view', ViewCandidateByIdView.as_view(), name='viewCandidate'),

    # * Settings (Ballot Position and Election Title)
    path("settings/ballot/position", BallotPositionView.as_view(), name='ballot_position'),
    path("settings/ballot/title/", BallotTitleView.as_view(), name='ballot_title'),

    # * Votes
    path('votes/view', ViewVotesView.as_view(), name='viewVotes'),
    #path('votes/reset/', views.resetVote, name='resetVote'),
    #path('votes/print/', views.PrintView.as_view(), name='printResult'),
]