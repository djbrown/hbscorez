from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('verknuepfen/', views.link, name='link'),
    path('entknuepfen/', views.unlink, name='unlink'),

    path('anmelden/', views.Login.as_view(), name='login'),
    path('abmelden/', views.Logout.as_view(), name='logout'),

    path('passwort-aendern/', views.PasswordChange.as_view(), name='password_change'),
    path('passwort-geaendert/', views.PasswordChangeSuccess.as_view(), name='password_change_success'),

    path('passwort-zuruecksetzen/', views.PasswordReset.as_view(), name='password_reset'),
    path('passwort-zurueckgesetzt/', views.PasswordResetSent.as_view(), name='password_reset_sent'),
    path('passwort-setzen/<uidb64>/<token>/', views.PasswordResetChange.as_view(), name='password_reset_change'),
    path('passwort-neu-gesetzt/', views.PasswordResetSuccess.as_view(), name='password_reset_success'),
]
