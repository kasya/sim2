from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Subject(models.Model):
  """Subject model."""

  name = models.CharField(max_length=1000)

  def __repr__(self):
    return f'<Name>: {self.name}'


class Exam(models.Model):
  """Exam model."""

  name = models.CharField(max_length=1000)
  subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
  passing_grade = models.IntegerField(default=75)
  duration_minutes = models.IntegerField(default=120)

  def __repr__(self):
    return f'<Name>: {self.name}'


class ExamAttempt(models.Model):
  """Exam attempt model."""

  IN_PROGRESS = 'in_progress'
  FINISHED = 'finished'

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
  created = models.DateTimeField(default=now, editable=False)
  grade = models.IntegerField(default=0)
  status = models.CharField(max_length=25, default=IN_PROGRESS)
  duration_minutes = models.IntegerField(default=0)

  questions = models.ManyToManyField('question.Question')

  def __repr__(self):
    return f'This exam attempt was created on {self.created} by {self.user}'


class AnswerAttempt(models.Model):
  """Answer attempt model."""

  attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
  question = models.ForeignKey('question.Question', on_delete=models.CASCADE)

  answers = models.ManyToManyField('question.Answer')

  def __repr__(self):
    return f'This is an answer attempt #{self.id} for an attempt #{self.attempt.id}'
