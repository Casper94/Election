from urllib.parse import urlparse
from django.urls import resolve
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
# from voting.models import Position, Candidate, Voter, Votes
from account.forms import CustomUserForm
from voting.forms import *
from django.http import JsonResponse


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
            return redirect('view_candidates')  # Redirect to the same view after successful form submission
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


class BallotPositionView(View):
    template_name = "admin/ballot_position.html"

    def get(self, request, *args, **kwargs):
        context = {
            'page_title': "Ballot Position"
        }
        return render(request, self.template_name, context)


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
            return redirect('view_positions')  # Redirect to the same view after successful form submission
        else:
            messages.error(request, "Form errors")

        return render(request, self.template_name, context)
