"""Exam models."""
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
  """Subject model."""

  name = models.CharField(verbose_name=_('name'), max_length=1000)
  class Meta:
    """Meta class for Subject model."""

    verbose_name = _('subject')
    verbose_name_plural = _('subjects')

  def __str__(self):
    return _('<Subject>: {name}, id# {id}').format(name=self.name, id=self.id)


class Exam(models.Model):
  """Exam model."""

  duration_minutes = models.IntegerField(verbose_name=_('duration'), default=120)
  name = models.CharField(verbose_name=_('name'), max_length=1000)
  passing_grade = models.IntegerField(verbose_name=_('grade'), default=75)
  subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
  question_count = models.IntegerField(verbose_name=_('question count'), default=50)
  class Meta:
    """Meta class for Exam model."""

    verbose_name = _('exam')
    verbose_name_plural = _('exams')

  def __str__(self):
    return _('<Exam>: {name}, id# {id}').format(name=self.name, id=self.id)


class ExamAttempt(models.Model):
  """Exam attempt model."""

  STATUS_FINISHED = 'finished'
  STATUS_IN_PROGRESS = 'in_progress'

  STATUSES = ((STATUS_FINISHED, _('Finished')), (STATUS_IN_PROGRESS,
                                              _('In progress')))

  PRACTICE_MODE = 'practice'
  EXAM_MODE = 'exam'

  EXAM_MODES = [

      (PRACTICE_MODE, _('Practice mode')),
      (EXAM_MODE, _('Exam mode')),
  ]

  created = models.DateTimeField(verbose_name=_('created'), default=timezone.now, editable=False)
  duration_minutes = models.IntegerField(verbose_name=_('duration'), default=120)
  grade = models.IntegerField(verbose_name=_('grade'), default=0)
  mode = models.CharField(verbose_name=_('mode'), max_length=30,
                          default=PRACTICE_MODE,
                          choices=EXAM_MODES)
  status = models.CharField(verbose_name=_('status'), max_length=25,
                            default=STATUS_IN_PROGRESS,
                            choices=STATUSES)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  exams = models.ManyToManyField(Exam)

  questions = models.ManyToManyField('question.Question')
  flagged_questions = models.ManyToManyField('question.Question',
                                             related_name='flagged_questions')
  class Meta:
    """Meta class for Exam Attempt model."""

    verbose_name = _('exam attempt')
    verbose_name_plural = _('exam attempts')

  def __str__(self):
    return _('<ExamAttempt>: id# {id}').format(id=self.id)

  @property
  def all_questions_answered(self):
    """Check if user answered all questions in current exam attempt."""

    return AnswerAttempt.objects.filter(
        attempt=self.id).count() == self.questions.count()

  @property
  def answered_question_ids(self):
    """Return all answered question ids for attempt."""
    return [
        answer_attempt.question.id
        for answer_attempt in AnswerAttempt.objects.filter(attempt=self.id)
    ]

  @property
  def is_in_exam_mode(self):
    """Check if exam attempt mode is exam."""
    return self.mode == self.EXAM_MODE

  @property
  def is_in_practice_mode(self):
    """Check if exam attempt mode is practice."""
    return self.mode == self.PRACTICE_MODE

  @property
  def is_subject_attempt(self):
    """Check if exam attempt is for a whole subject."""
    return self.exam.count() > 1

  @property
  def is_exam_attempt(self):
    """Check if exam attempt is for a specific exam in subject."""
    return self.exam.count() == 1

  @property
  def passed(self):
    """Check if user passed exam."""

    passing_grade = (sum([exam.passing_grade for exam in self.exams.all()]) /
                     self.exams.count())
    return self.grade >= passing_grade

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

      answer_attempt_count = answer_attempts.count()
      if answer_attempt_count:
        grade = round(correct_answer_count / answer_attempt_count * 100)

    self.grade = grade
    self.save()
    return grade

  def save(self, *args, **kwargs):
    """Add user required extra time to attempt duration and save attempt."""

    if not self.id:
      self.duration_minutes += self.user.required_extra_time

    super().save(*args, **kwargs)


class AnswerAttempt(models.Model):
  """Answer attempt model."""

  attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
  question = models.ForeignKey('question.Question', on_delete=models.CASCADE)

  answers = models.ManyToManyField('question.Answer')
  class Meta:
    """Meta class for Answer Attempt model."""

    verbose_name = _('answer attempt')
    verbose_name_plural = _('answer attempts')

  def __str__(self):
    return _('<AnswerAttempt>: id# {id}').format(id=self.id)
