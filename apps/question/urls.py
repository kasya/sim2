"""Question app URL configuration."""

from django.urls import path
from django.views.generic import TemplateView

from apps.question.views import QuestionView

urlpatterns = [
    path('api/attempt/<int:attempt_id>/question/',
         QuestionView.as_view(),
         name='question_api'),
]
