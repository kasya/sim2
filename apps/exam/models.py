"""Exam models."""
from django.conf import settings
from django.db import models
from django.utils.timezone import now


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

  STATUS_IN_PROGRESS = 'in_progress'
  STATUS_FINISHED = 'finished'

  STATUSES = ((STATUS_IN_PROGRESS, 'In progress'), (STATUS_FINISHED,
                                                    'Finished'))

  created = models.DateTimeField(default=now, editable=False)
  duration_minutes = models.IntegerField(default=0)
  grade = models.IntegerField(default=0)
  status = models.CharField(max_length=25,
                            default=STATUS_IN_PROGRESS,
                            choices=STATUSES)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

  questions = models.ManyToManyField('question.Question')

  def __str__(self):
    return f'<ExamAttempt>: id# {self.id}'


class AnswerAttempt(models.Model):
  """Answer attempt model."""

  attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
  question = models.ForeignKey('question.Question', on_delete=models.CASCADE)

  answers = models.ManyToManyField('question.Answer')

  def __str__(self):
    return f'<AnswerAttempt>: id# {self.id}'
