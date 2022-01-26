"""Exam app URL configuration."""

from django.urls import path
from django.views.generic import TemplateView

from apps.exam.models import Exam
from apps.exam.serializers import ExamSerializer
from apps.exam.views import (ExamFinishView, ExamIntro, ExamList, ExamPageView,
                             SubjectList)

urlpatterns = [
    path(
        'start/',
        TemplateView.as_view(
            template_name='exam/subject.html',
            extra_context={'api_url': 'http://127.0.0.1:8000/'})),
    path('api/subject/', SubjectList.as_view(), name='subject_list'),
    path('api/subject/<subject_id>/exams/',
         ExamList.as_view(),
         name='exam_list'),
    path('exam/<exam_id>/intro/', ExamIntro.as_view(), name='exam_intro'),
    path('exam/<exam_id>/<attempt_id>/',
         ExamPageView.as_view(),
         name='exam_page'),
    path('exam/<attempt_id>/finish',
         ExamFinishView.as_view(),
         name='exam_finish'),
]
