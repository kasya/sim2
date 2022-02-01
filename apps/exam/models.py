"""Exam models."""
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import now

from apps.question.models import Question


class Subject(models.Model):
  """Subject model."""

  name = models.CharField(max_length=1000)

  def __str__(self):
    return f'<Subject>: {self.name}, id# {self.id}'


class Exam(models.Model):
  """Exam model."""

  duration_minutes = models.IntegerField(default=120)
  name = models.CharField(max_length=1000)
  passing_grade = models.IntegerField(default=75)
  subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

  def __str__(self):
    return f'<Exam>: {self.name}, id# {self.id}'


class ExamAttempt(models.Model):
  """Exam attempt model."""

  STATUS_FINISHED = 'finished'
  STATUS_IN_PROGRESS = 'in_progress'

  STATUSES = ((STATUS_FINISHED, 'Finished'), (STATUS_IN_PROGRESS,
                                              'In progress'))

  created = models.DateTimeField(default=timezone.now, editable=False)
  duration_minutes = models.IntegerField(default=120)
  grade = models.IntegerField(default=0)
  status = models.CharField(max_length=25,
                            default=STATUS_IN_PROGRESS,
                            choices=STATUSES)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

  questions = models.ManyToManyField('question.Question')

  def __str__(self):
    return f'<ExamAttempt>: id# {self.id}'

  @property
  def all_questions_answered(self):
    """Check if user answered all questions in current exam attempt."""

    return AnswerAttempt.objects.filter(
        attempt=self.id).count() == self.questions.count()

  @property
  def time_left_seconds(self):
    """Calculate how much time left in exam attempt until the end."""

    end_time = self.created + timedelta(minutes=self.duration_minutes)
    time_left = end_time - timezone.now()
    return max(int(time_left.total_seconds()), 0)

  def calculate_grade(self):
    """Calculate the grade for an attempt."""

    correct_answer_count = 0
    grade = 0
    answer_attempts = AnswerAttempt.objects.filter(attempt=self.id)
    question_ids = [a.question.id for a in answer_attempts]

    for answer_attempt in AnswerAttempt.objects.filter(
        question_id__in=question_ids,
        attempt=self.id).select_related('question').prefetch_related('answers'):

      if set((a.id for a in answer_attempt.answers.all())) == set(
          answer_attempt.question.correct_answer_ids()):
        correct_answer_count += 1

    grade = round(correct_answer_count / answer_attempts.count() * 100)

    self.grade = grade
    self.save()

    return grade


class AnswerAttempt(models.Model):
  """Answer attempt model."""

  attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
  question = models.ForeignKey('question.Question', on_delete=models.CASCADE)

  answers = models.ManyToManyField('question.Answer')

  def __str__(self):
    return f'<AnswerAttempt>: id# {self.id}'
