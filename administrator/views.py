from urllib.parse import urlparse
from django.urls import resolve
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings
from account.forms import CustomUserForm
from voting.forms import *
from django.urls import reverse
from django.http import JsonResponse


class AdminDashboardView(View):
    template_name = "admin/home.html"

    def get(self, request, *args, **kwargs):
        positions = Position.objects.all().order_by('priority')
        candidates = Candidate.objects.all()
        voters = Voter.objects.all()
        voted_voters = Voter.objects.filter(voted=1)
        chart_data = {}

        for position in positions:
            list_of_candidates = []
            votes_count = []
            for candidate in Candidate.objects.filter(position=position):
                list_of_candidates.append(candidate.fullname)
                votes = Votes.objects.filter(candidate=candidate).count()
                votes_count.append(votes)
            chart_data[position] = {
                'candidates': list_of_candidates,
                'votes': votes_count,
                'pos_id': position.id
            }

        context = {
            'position_count': positions.count(),
            'candidate_count': candidates.count(),
            'voters_count': voters.count(),
            'voted_voters_count': voted_voters.count(),
            'positions': positions,
            'chart_data': chart_data,
            'page_title': "Dashboard"
        }
        return render(request, self.template_name, context)


class VotersView(View):
    template_name = "admin/voters.html"

    def get(self, request, *args, **kwargs):
        voters = Voter.objects.all()
        user_form = CustomUserForm()
        voter_form = VoterForm()
        context = {
            'form1': user_form,
            'form2': voter_form,
            'voters': voters,
            'page_title': 'Voters List'
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = CustomUserForm(request.POST)
        voter_form = VoterForm(request.POST)
        voters = Voter.objects.all()
        context = {
            'form1': user_form,
            'form2': voter_form,
            'voters': voters,
            'page_title': 'Voters List'
        }

        if user_form.is_valid() and voter_form.is_valid():
            user = user_form.save(commit=False)
            voter = voter_form.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
            return redirect('voters')  # Redirect to the same view after successful form submission
        else:
            messages.error(request, "Form validation failed")

        return render(request, self.template_name, context)


class ViewVotesView(View):
    template_name = "admin/votes.html"

    def get(self, request, *args, **kwargs):
        votes = Votes.objects.all()
        context = {
            'votes': votes,
            'page_title': 'Votes'
        }
        return render(request, self.template_name, context)


class ViewVoterByIdView(View):
    def get(self, request, *args, **kwargs):
        voter_id = request.GET.get('id', None)
        voter = Voter.objects.filter(id=voter_id)
        context = {}

        if not voter.exists():
            context['code'] = 404
        else:
            context['code'] = 200
            voter = voter[0]
            context['first_name'] = voter.admin.first_name
            context['last_name'] = voter.admin.last_name
            context['phone'] = voter.phone
            context['id'] = voter.id
            context['email'] = voter.admin.email

        return JsonResponse(context)


class UpdateVoterView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, 'Access Denied')
            return redirect(reverse('adminViewVoters'))

        try:
            instance = Voter.objects.get(id=request.POST.get('id'))
            user_form = CustomUserForm(request.POST or None, instance=instance.admin)
            voter_form = VoterForm(request.POST or None, instance=instance)

            if user_form.is_valid() and voter_form.is_valid():
                user_form.save()
                voter_form.save()
                messages.success(request, 'Voter\'s bio updated')
            else:
                messages.error(request, "Form validation Failed.")
        except Voter.DoesNotExist:
            messages.error(request, "Access to this Resource Denied")
        return redirect(reverse('adminViewVoters'))


class DeleteVoterView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, "Access Denied")
            return redirect(reverse('adminViewVoters'))

        try:
            voter = Voter.objects.get(id=request.POST.get('id'))
            admin = voter.admin
            admin.delete()
            messages.success(request, "Voter has been deleted")
        except Voter.DoesNotExist:
            messages.error(request, "Access to this resource denied")

        return redirect(reverse('adminViewVoters'))


class ViewPositionByIdView(View):
    def get(self, request, *args, **kwargs):
        pos_id = request.GET.get('id', None)
        position = Position.objects.filter(id=pos_id)
        context = {}

        if not position.exists():
            context['code'] = 404
        else:
            context['code'] = 200
            position = position.first()
            context['name'] = position.name
            context['max_vote'] = position.max_vote
            context['id'] = position.id

        return JsonResponse(context)


class ViewPositionsView(View):
    template_name = "admin/positions.html"

    def get(self, request, *args, **kwargs):
        positions = Position.objects.order_by('-priority').all()
        form = PositionForm()
        context = {
            'positions': positions,
            'form1': form,
            'page_title': "Positions"
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = PositionForm(request.POST)
        positions = Position.objects.order_by('-priority').all()
        context = {
            'positions': positions,
            'form1': form,
            'page_title': "Positions"
        }

        if form.is_valid():
            new_position = form.save(commit=False)
            new_position.priority = positions.count() + 1  # Just in case it is empty.
            new_position.save()
            messages.success(request, "New Position Created")
            return redirect('viewPositions')  # Redirect to the same view after successful form submission
        else:
            messages.error(request, "Form errors")

        return render(request, self.template_name, context)


class UpdatePositionView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, "Access Denied")
            return redirect(reverse('viewPositions'))

        try:
            instance = Position.objects.get(id=request.POST.get('id'))
            position_form = PositionForm(request.POST or None, instance=instance)

            if position_form.is_valid():
                position_form.save()
                messages.success(request, "Position has been updated")
            else:
                messages.error(request, "Form validation failed")

        except Position.DoesNotExist:
            messages.error(request, "Access to this resource denied")

        return redirect(reverse('viewPositions'))


class DeletePositionView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, "Access Denied")
            return redirect(reverse('viewPositions'))

        try:
            position = Position.objects.get(id=request.POST.get('id'))
            position.delete()
            messages.success(request, "Position has been deleted")
        except Position.DoesNotExist:
            messages.error(request, "Access to this resource denied")

        return redirect(reverse('viewPositions'))


class ViewCandidatesView(View):
    template_name = "admin/candidates.html"

    def get(self, request, *args, **kwargs):
        candidates = Candidate.objects.all()
        form = CandidateForm()
        context = {
            'candidates': candidates,
            'form1': form,
            'page_title': 'Candidates'
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = CandidateForm(request.POST, request.FILES)
        candidates = Candidate.objects.all()
        context = {
            'candidates': candidates,
            'form1': form,
            'page_title': 'Candidates'
        }

        if form.is_valid():
            new_candidate = form.save()
            messages.success(request, "New Candidate Created")
            return redirect('viewCandidates')  # Redirect to the same view after successful form submission
        else:
            messages.error(request, "Form errors")

        return render(request, self.template_name, context)


class ViewCandidateByIdView(View):
    def get(self, request, *args, **kwargs):
        candidate_id = request.GET.get('id', None)
        candidate = Candidate.objects.filter(id=candidate_id)
        context = {}

        if not candidate.exists():
            context['code'] = 404
        else:
            candidate = candidate[0]
            context['code'] = 200
            context['fullname'] = candidate.fullname
            previous = CandidateForm(instance=candidate)
            context['form'] = str(previous.as_p())

        return JsonResponse(context)


class UpdateCandidateView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, "Access Denied")
            return redirect(reverse('viewCandidates'))

        try:
            candidate_id = request.POST.get('id')
            candidate = Candidate.objects.get(id=candidate_id)
            form = CandidateForm(request.POST or None, request.FILES or None, instance=candidate)

            if form.is_valid():
                form.save()
                messages.success(request, "Candidate Data Updated")
            else:
                messages.error(request, "Form has errors")

        except Candidate.DoesNotExist:
            messages.error(request, "Access To This Resource Denied")

        return redirect(reverse('viewCandidates'))


class DeleteCandidateView(View):
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            messages.error(request, "Access Denied")
            return redirect(reverse('viewCandidates'))

        try:
            candidate = Candidate.objects.get(id=request.POST.get('id'))
            candidate.delete()
            messages.success(request, "Candidate has been deleted")
        except Candidate.DoesNotExist:
            messages.error(request, "Access to this resource denied")

        return redirect(reverse('viewCandidates'))


class BallotPositionView(View):
    template_name = "admin/ballot_position.html"

    def get(self, request, *args, **kwargs):
        context = {
            'page_title': "Ballot Position"
        }
        return render(request, self.template_name, context)


class UpdateBallotPositionView(View):
    def get(self, request, position_id, up_or_down, *args, **kwargs):
        try:
            context = {'error': False}
            position = Position.objects.get(id=position_id)

            if up_or_down == 'up':
                priority = position.priority - 1
                if priority == 0:
                    context['error'] = True
                    output = "This position is already at the top"
                else:
                    Position.objects.filter(priority=priority).update(priority=(priority + 1))
                    position.priority = priority
                    position.save()
                    output = "Moved Up"
            else:
                priority = position.priority + 1
                if priority > Position.objects.all().count():
                    output = "This position is already at the bottom"
                    context['error'] = True
                else:
                    Position.objects.filter(priority=priority).update(priority=(priority - 1))
                    position.priority = priority
                    position.save()
                    output = "Moved Down"

            context['message'] = output
        except Exception as e:
            context['message'] = str(e)

        return JsonResponse(context)


class BallotTitleView(View):
    def post(self, request, *args, **kwargs):
        try:
            url = urlparse(request.META['HTTP_REFERER']).path
            redirect_url = resolve(url)
            title = request.POST.get('title', 'No Name')
            with open(settings.ELECTION_TITLE_PATH, 'w') as file:
                file.write(title)
            messages.success(request, "Election title has been changed to " + str(title))
            return redirect(url)
        except Exception as e:
            messages.error(request, str(e))
            return redirect("/")


class ResetVoteView(View):
    def get(self, request, *args, **kwargs):
        Votes.objects.all().delete()
        Voter.objects.all().update(voted=False, verified=False, otp=None)
        messages.success(request, "All votes have been reset")
        return redirect(reverse('viewVotes'))