from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from .forms import CustomUserForm
from voting.forms import VoterForm



# Create your views here.
class AccountLoginView(View):
    template_name = "voting/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))

        context = {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = self.authenticate_user(request.POST.get('email'), request.POST.get('password'))

        if user is not None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")

    def authenticate_user(self, username, password):
        return ModelBackend().authenticate(username=username, password=password)


class AccountRegisterView(View):
    template_name = "voting/register.html"

    def get(self, request, *args, **kwargs):
        user_form = CustomUserForm()
        voter_form = VoterForm()
        context = {'form1': user_form, 'form2': voter_form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = CustomUserForm(request.POST)
        voter_form = VoterForm(request.POST)
        context = {'form1': user_form, 'form2': voter_form}

        if user_form.is_valid() and voter_form.is_valid():
            user = user_form.save(commit=False)
            voter = voter_form.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")

        return render(request, self.template_name, context)
