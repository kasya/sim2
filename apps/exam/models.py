"""Exam models."""
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


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
  question_count = models.IntegerField(default=50)

  def __str__(self):
    return f'<Exam>: {self.name}, id# {self.id}'


class ExamAttempt(models.Model):
  """Exam attempt model."""

  STATUS_FINISHED = 'finished'
  STATUS_IN_PROGRESS = 'in_progress'

  STATUSES = ((STATUS_FINISHED, 'Finished'), (STATUS_IN_PROGRESS,
                                              'In progress'))

  PRACTICE_MODE = 'practice'
  EXAM_MODE = 'exam'

  EXAM_MODES = [
      (PRACTICE_MODE, 'Practice mode'),
      (EXAM_MODE, 'Exam mode'),
  ]

  created = models.DateTimeField(default=timezone.now, editable=False)
  duration_minutes = models.IntegerField(default=120)
  grade = models.IntegerField(default=0)
  mode = models.CharField(max_length=30,
                          default=PRACTICE_MODE,
                          choices=EXAM_MODES)
  status = models.CharField(max_length=25,
                            default=STATUS_IN_PROGRESS,
                            choices=STATUSES)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  exams = models.ManyToManyField(Exam)

  questions = models.ManyToManyField('question.Question')
  flagged_questions = models.ManyToManyField('question.Question',
                                             related_name='flagged_questions')

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

  def __str__(self):
    return f'<ExamAttempt>: id# {self.id}'

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

  def __str__(self):
    return f'<AnswerAttempt>: id# {self.id}'
