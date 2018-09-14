from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('password-change/', views.PasswordChange.as_view(), name='password_change'),
    path('password-change/success/', views.PasswordChangeSuccess.as_view(), name='password_change_success'),

    path('password-reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password-reset/sent/', views.PasswordResetSent.as_view(), name='password_reset_sent'),
    path('password-reset/<uidb64>/<token>/', views.PasswordResetChange.as_view(), name='password_reset_change'),
    path('password-reset/success/', views.PasswordResetSuccess.as_view(), name='password_reset_success'),
]
