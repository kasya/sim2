"""Exam views methods."""

import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exam.models import Exam, ExamAttempt, Subject
from apps.exam.serializers import (ExamAttemptSerializer, ExamSerializer,
                                   SubjectSerializer)
from apps.question.models import Question


class SubjectList(APIView):
  """Retrieve a list of all subjects."""

  permission_classes = (IsAuthenticated,)

  def get(self, request):
    return Response(SubjectSerializer(Subject.objects.all(), many=True).data)


class ExamList(APIView):
  """Retrieve a list of all exams."""

  permission_classes = (IsAuthenticated,)

  def get(self, request, subject_id):
    """Pre-populating select menu with possible exams for chosen subject."""
    return Response(
        ExamSerializer(Exam.objects.filter(subject=subject_id), many=True).data)


class ExamIntro(LoginRequiredMixin, TemplateView):

  template_name = 'exam/exam_intro.html'

  def get_context_data(self, **kwargs):
    """Render intro page template for chosen exam. """

    context = super().get_context_data(**kwargs)
    if 'exam_id' in self.kwargs:
      exam = Exam.objects.filter(id=self.kwargs['exam_id'])
      context['subject'] = Subject.objects.get(exam=exam[0])
      context['exam'] = exam[0]

    if 'subject_id' in self.kwargs:
      context['subject'] = Subject.objects.get(id=self.kwargs['subject_id'])
      exam = Exam.objects.filter(subject_id=self.kwargs['subject_id'])
      context['subject_question_count'] = 50

    context['attempt_duration'] = int(
        sum([e.duration_minutes for e in exam]) / len(exam) +
        self.request.user.required_extra_time)
    context['exam_mode'] = self.kwargs['exam_mode']

    return context

  def post(self, request, exam_mode, subject_id=None, exam_id=None):
    """
    Create an attempt entity with chosen exam_id.
    Pre-populate attempt_questions table with questions from this exam.
    """
    if subject_id:
      exams = Exam.objects.filter(subject_id=subject_id)
      current_attempt = ExamAttempt.objects.create(
          user=request.user, mode=self.kwargs['exam_mode'])
      current_attempt.exam.set(exams)
      question_pool_ids = []
      for exam in exams:
        question_pool_ids.extend(
            Question.objects.filter(exam=exam).values_list('id', flat=True))
      if len(question_pool_ids) > 50:
        question_pool_ids = random.sample(question_pool_ids, 50)

    elif exam_id:
      exam = Exam.objects.get(id=exam_id)
      current_attempt = ExamAttempt.objects.create(
          user=request.user, mode=self.kwargs['exam_mode'])
      current_attempt.exam.set(Exam.objects.filter(id=exam_id))

      question_pool_ids = [question.id for question in exam.questions.all()]
      if exam.questions.count() > exam.question_count:
        question_pool_ids = random.sample(question_pool_ids,
                                          exam.question_count)

    current_attempt.questions.set(
        Question.objects.filter(id__in=question_pool_ids))

    return redirect(reverse('exam_page', args=[current_attempt.id]))


class ExamPageView(TemplateView, LoginRequiredMixin):

  template_name = 'exam/exam_attempt.html'

  def get_context_data(self, **kwargs):
    """Render page with actual questions. """

    context = super().get_context_data(**kwargs)
    context['attempt'] = ExamAttempt.objects.get(id=self.kwargs['attempt_id'])
    return context


class ExamFinishView(TemplateView, LoginRequiredMixin):

  template_name = 'exam/finish.html'

  def get_context_data(self, **kwargs):
    """Show grade for the exam and in case of failure
       suggest to give it another try.
    """

    try:
      current_attempt = ExamAttempt.objects.get(id=self.kwargs['attempt_id'],
                                                user=self.request.user)
    except ExamAttempt.DoesNotExist:
      raise Http404

    if not current_attempt.all_questions_answered:
      raise Http404

    current_attempt.status = ExamAttempt.STATUS_FINISHED
    current_attempt.save()
    exams = current_attempt.exam.all()

    context = super().get_context_data(**kwargs)

    context['grade'] = current_attempt.calculate_grade()
    context['passing_grade'] = int(
        sum([exam.passing_grade for exam in exams]) /
        len(current_attempt.exam.all()))
    if current_attempt.passed:
      context[
          'status'] = f"Congratulations! You've finished {current_attempt.mode} in {exams[0].subject.name} {exams[0].name}! Your grade is {current_attempt.grade}%."
    else:
      context[
          'status'] = f"Sorry, you haven't passed the {exams[0].subject.name} {exams[0].name} {current_attempt.mode}. Your grade is {current_attempt.grade}%."

    return context


class AttemptView(APIView):

  permission_classes = (IsAuthenticated,)

  def get(self, request, attempt_id):
    """Returns exam attempt."""

    try:
      return Response(
          ExamAttemptSerializer(ExamAttempt.objects.get(id=attempt_id)).data)

    except ExamAttempt.DoesNotExist:
      raise Http404


class QuestionFlag(APIView):
  """Question flagging view."""

  def post(self, request, **kwargs):
    """Add or remove question id from flagged_questions."""

    attempt = get_object_or_404(ExamAttempt,
                                id=self.kwargs['attempt_id'],
                                user=request.user.id)
    question = get_object_or_404(Question, id=self.kwargs['question_id'])

    if attempt.flagged_questions.filter(id=question.id).exists():
      attempt.flagged_questions.remove(question)
    else:
      attempt.flagged_questions.add(question)

    return Response(ExamAttemptSerializer(attempt).data)
