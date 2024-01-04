from django.urls import path
from .views import *


urlpatterns = [
    path('', AdminDashboardView.as_view(), name="adminDashboard"),

    # * Voters
    path('voters/', VotersView.as_view(), name='adminViewVoters'),
    path('voters/view', ViewVoterByIdView.as_view(), name="viewVoter"),
    path('voters/delete', DeleteVoterView.as_view(), name='deleteVoter'),
    path('voters/update', UpdateVoterView.as_view(), name="updateVoter"),

    # * Position
    path('position/view', ViewPositionByIdView.as_view(), name='viewPosition'),
    path('position/update', UpdatePositionView.as_view(), name="updatePosition"),
    path('position/delete', DeletePositionView.as_view(), name='deletePosition'),
    path('positions/view', ViewPositionsView.as_view(), name='viewPositions'),

    # * Candidate
    path('candidate/', ViewCandidatesView.as_view(), name='viewCandidates'),
    path('candidate/view', ViewCandidateByIdView.as_view(), name='viewCandidate'),
    path('candidate/update', UpdateCandidateView.as_view, name="updateCandidate"),
    path('candidate/delete', DeleteCandidateView.as_view(), name='deleteCandidate'),

    # * Settings (Ballot Position and Election Title)
    path("settings/ballot/position", BallotPositionView.as_view(), name='ballot_position'),
    path("settings/ballot/title/", BallotTitleView.as_view(), name='ballot_title'),
    path("settings/ballot/position/update/<int:position_id>/<str:up_or_down>/",
         UpdateBallotPositionView.as_view(), name='update_ballot_position'),

    # * Votes
    path('votes/view', ViewVotesView.as_view(), name='viewVotes'),
    path('votes/reset/', ResetVoteView.as_view(), name='resetVote'),
    #path('votes/print/', views.PrintView.as_view(), name='printResult'),
]