from typing import Dict

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from associations.models import Association
from leagues.models import Season
from players.models import Player
from teams.models import Team

from .forms import LinkForm


@login_required
def profile(request):
    players = Player.objects.filter(user=request.user)
    return render(request=request, template_name='users/profile.html', context={'players': players})


@login_required
def link(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        team = team_from_request_query(request.POST)
        if form.is_valid():
            player = form.cleaned_data.get('player')
            player.user = request.user
            player.published = True
            player.save()

            profile_url = reverse_lazy('users:profile')
            return HttpResponseRedirect(profile_url)

    else:
        form = LinkForm(user=request.user)
        team = team_from_request_query(request.GET)

    return render(request=request, template_name='users/link.html', context={
        'form': form,
        'team': team,
        'seasons': Season.objects.all(),
        'associations': Association.objects.all(),
    })


def team_from_request_query(query)-> Dict:
    team_bhv_id = query.get('team_bhv_id')
    try:
        return Team.objects.get(bhv_id=team_bhv_id)
    except ObjectDoesNotExist:
        return None


class Link(auth_views.LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class Login(auth_views.LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class Logout(auth_views.LogoutView):
    template_name = 'users/logout.html'


class PasswordChange(auth_views.PasswordChangeView):
    success_url = reverse_lazy('users:password_change_success')
    template_name = 'users/password-change.html'


class PasswordChangeSuccess(auth_views.PasswordChangeDoneView):
    template_name = 'users/password-change-success.html'


class PasswordReset(auth_views.PasswordResetView):
    email_template_name = 'users/password-reset-email.html'
    subject_template_name = 'users/password-reset-email-subject.txt'
    success_url = reverse_lazy('users:password_reset_sent')
    template_name = 'users/password-reset.html'


class PasswordResetSent(auth_views.PasswordResetDoneView):
    template_name = 'users/password-reset-sent.html'


class PasswordResetChange(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_success')
    template_name = 'users/password-reset-change.html'


class PasswordResetSuccess(auth_views.PasswordResetCompleteView):
    template_name = 'users/password-reset-success.html'
