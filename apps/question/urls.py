"""Question app URL configuration."""

from django.urls import path

from apps.question.views import QuestionAnswerView, QuestionView

urlpatterns = [
    path('api/attempt/<int:attempt_id>/question/',
         QuestionView.as_view(),
         name='question_api'),
    path('api/attempt/<int:attempt_id>/<int:question_id>/',
         QuestionAnswerView.as_view(),
         name='question_answers_api'),
]
