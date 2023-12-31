from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.views import View
from .models import Votes
# from .utils import bypass_otp

# Create your views here.
class VoterDashboardView(View):
    template_name = "voting/voter/result.html"

    # def get(self, request, *args, **kwargs):
    #     user = request.user
    #
    #     # Check if this voter has been verified
    #     if user.voter.otp is None or user.voter.verified is False:
    #         if not settings.SEND_OTP:
    #             # Bypass
    #             msg = bypass_otp()
    #             messages.success(request, msg)
    #             return redirect(reverse('show_ballot'))
    #         else:
    #             return redirect(reverse('voterVerify'))
    #     else:
    #         if user.voter.voted:
    #             # User has voted
    #             context = {
    #                 'my_votes': Votes.objects.filter(voter=user.voter),
    #             }
    #             return render(request, self.template_name, context)
    #         else:
    #             return redirect(reverse('show_ballot'))