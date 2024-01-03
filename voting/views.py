from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.views import View
from .models import *
#from .utils import bypass_otp
from django.http import JsonResponse
from django.utils.text import slugify
from .mixins import BallotGeneratorMixin


# Create your views here.
class VoterDashboardView(View):
    template_name = "voting/voter/result.html"

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if this voter has been verified
        if user.voter.otp is None or user.voter.verified is False:
            if not settings.SEND_OTP:
                # Bypass
                msg = self.bypass_otp()
                messages.success(request, msg)
                return redirect(reverse('show_ballot'))
            else:
                return redirect(reverse('voterVerify'))
        else:
            if user.voter.voted:
                # User has voted
                context = {
                    'my_votes': Votes.objects.filter(voter=user.voter),
                }
                return render(request, self.template_name, context)
            else:
                return redirect(reverse('show_ballot'))

    def bypass_otp(self):  # done
        Voter.objects.all().filter(otp=None, verified=False).update(otp="0000", verified=True)
        response = "Kindly cast your vote"
        return response


class BypassOTPView(View):
    def get(self, request, *args, **kwargs):
        Voter.objects.filter(otp=None, verified=False).update(otp="0000", verified=True)
        response = "Kindly cast your vote"
        return JsonResponse({'message': response})


class ShowBallotView(BallotGeneratorMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.voter.voted:
            messages.error(request, "You have voted already")
            return redirect(reverse('voterDashboard'))
        positions = Position.objects.order_by('priority').all()
        ballot = self.generate_ballot(positions, display_controls=False)

        context = {
            'ballot': ballot
        }

        return render(request, "voting/voter/ballot.html", context)


class FetchBallotView(BallotGeneratorMixin, View):
    def get(self, request, *args, **kwargs):
        positions = Position.objects.order_by('priority').all()
        output = self.generate_ballot(positions, display_controls=True)
        return JsonResponse(output, safe=False)


class PreviewVoteView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            error = True
            response = "Please browse the system properly"
        else:
            output = ""
            form = dict(request.POST)
            # We don't need to loop over CSRF token
            form.pop('csrfmiddlewaretoken', None)
            error = False
            data = []
            positions = Position.objects.all()

            for position in positions:
                max_vote = position.max_vote
                pos = slugify(position.name)
                pos_id = position.id

                if position.max_vote > 1:
                    this_key = pos + "[]"
                    form_position = form.get(this_key)

                    if form_position is None:
                        continue

                    if len(form_position) > max_vote:
                        error = True
                        response = f"You can only choose {max_vote} candidates for {position.name}"
                    else:
                        start_tag = f"""
                           <div class='row votelist' style='padding-bottom: 2px'>
                               <span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
                               <span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>


                        """
                        end_tag = "</ul></span></div><hr/>"
                        data = ""

                        for form_candidate_id in form_position:
                            try:
                                candidate = Candidate.objects.get(
                                    id=form_candidate_id, position=position)
                                data += f"""
                                   <li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                                """
                            except:
                                error = True
                                response = "Please, browse the system properly"
                        output += start_tag + data + end_tag
                else:
                    this_key = pos
                    form_position = form.get(this_key)

                    if form_position is None:
                        continue

                    # Max Vote == 1
                    try:
                        form_position = form_position[0]
                        candidate = Candidate.objects.get(
                            position=position, id=form_position)
                        output += f"""
                                <div class='row votelist' style='padding-bottom: 2px'>
                                   <span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
                                   <span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
                                </div>
                              <hr/>
                            """
                    except Exception as e:
                        error = True
                        response = "Please, browse the system properly"

        context = {
            'error': error,
            'list': output
        }

        return JsonResponse(context, safe=False)


class SubmitBallotView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, "Please, browse the system properly")
            return redirect(reverse('show_ballot'))

        # Verify if the voter has voted or not
        voter = request.user.voter
        if voter.voted:
            messages.error(request, "You have voted already")
            return redirect(reverse('voterDashboard'))

        form = dict(request.POST)
        form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
        form.pop('submit_vote', None)  # Pop Submit Button

        # Ensure at least one vote is selected
        if len(form.keys()) < 1:
            messages.error(request, "Please select at least one candidate")
            return redirect(reverse('show_ballot'))

        positions = Position.objects.all()
        form_count = 0

        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id

            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue

                if len(form_position) > max_vote:
                    messages.error(
                        request, f"You can only choose {max_vote} candidates for {position.name}")
                    return redirect(reverse('show_ballot'))
                else:
                    for form_candidate_id in form_position:
                        form_count += 1
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position)
                            vote = Votes()
                            vote.candidate = candidate
                            vote.voter = voter
                            vote.position = position
                            vote.save()
                        except Exception as e:
                            messages.error(
                                request, "Please, browse the system properly " + str(e))
                            return redirect(reverse('show_ballot'))
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue

                # Max Vote == 1
                form_count += 1
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    vote = Votes()
                    vote.candidate = candidate
                    vote.voter = voter
                    vote.position = position
                    vote.save()
                except Exception as e:
                    messages.error(
                        request, "Please, browse the system properly " + str(e))
                    return redirect(reverse('show_ballot'))

        # Count total number of records inserted
        # Check it viz-a-viz form_count
        inserted_votes = Votes.objects.filter(voter=voter)

        if inserted_votes.count() != form_count:
            # Delete
            inserted_votes.delete()
            messages.error(request, "Please try voting again!")
            return redirect(reverse('show_ballot'))
        else:
            # Update Voter profile to voted
            voter.voted = True
            voter.save()
            messages.success(request, "Thanks for voting")
            return redirect(reverse('voterDashboard'))