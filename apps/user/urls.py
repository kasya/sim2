"""User app URL configuration."""

from django.urls import path

from apps.user import views

urlpatterns = [
    path('login', views.Login.as_view(), name='login'),
    path('profile', views.Profile.as_view(), name='profile'),
    path('signup', views.Signup.as_view(), name='signup'),
    path('logout', views.Logout.as_view(), name='logout'),
]
