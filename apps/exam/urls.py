"""Exam app URL configuration."""

from django.urls import path
from django.views.generic import TemplateView

from apps.exam.views import (
    AttemptView,
    ExamFinishView,
    ExamIntro,
    ExamList,
    ExamPageView,
    QuestionFlag,
    SubjectList,
)

urlpatterns = [
    path(
        "start/",
        TemplateView.as_view(template_name="exam/subject.html"),
        name="start",
    ),
    path("api/subject/", SubjectList.as_view(), name="subject_list"),
    path(
        "api/subject/<subject_id>/exams/", ExamList.as_view(), name="exam_list"
    ),
    path(
        "exam/<exam_id>/<exam_mode>/intro/",
        ExamIntro.as_view(),
        name="exam_intro",
    ),
    path(
        "exam/subject/<subject_id>/<exam_mode>/intro/",
        ExamIntro.as_view(),
        name="exam_intro",
    ),
    path("exam/<attempt_id>/", ExamPageView.as_view(), name="exam_page"),
    path(
        "exam/<attempt_id>/finish",
        ExamFinishView.as_view(),
        name="exam_finish",
    ),
    path(
        "api/attempt/<attempt_id>/", AttemptView.as_view(), name="get_attempt"
    ),
    path(
        "api/attempt/<int:attempt_id>/<int:question_id>/flag",
        QuestionFlag.as_view(),
        name="question_toggle_flag",
    ),
]
