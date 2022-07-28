"""User app URL configuration."""

from django.urls import path

from apps.user import views

urlpatterns = [
    path('login', views.Login.as_view(), name='login'),
    path('profile', views.Profile.as_view(), name='profile'),
    path('signup', views.Signup.as_view(), name='signup'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('api/progress/<int:exam_id>',
         views.ProfileChart.as_view(),
         name='profile-chart'),
    path('profile/progress-charts',
         views.ProgressCharts.as_view(),
         name='progress-charts'),
    path('profile/edit', views.EditProfile.as_view(), name='edit-profile'),
]
