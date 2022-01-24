"""Tests for Exam app models."""

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject
from apps.question.models import Answer, Question, QuestionCategory
from apps.user.models import User
from django.test import TestCase


class ExamModelTestCase(TestCase):
  """Test cases for exam models."""

  def setUp(self):

    subject = Subject.objects.create(name='Subject 1')
    exam = Exam.objects.create(name='Exam 1', subject=subject)
    user = User.objects.create_user(username='John', password='password')
    exam_attempt = ExamAttempt.objects.create(user=user, exam=exam)
    correct_answers = Answer.objects.create(text='Answer 1')
    wrong_answers = Answer.objects.create(text='Answer 2')
    question_category = QuestionCategory.objects.create(name='Category 1')
    question = Question.objects.create(category=question_category,
                                       text='Question 1',
                                       exam=exam)
    question.correct_answers.add(correct_answers)
    question.wrong_answers.add(wrong_answers)

    answer_attempt = AnswerAttempt.objects.create(attempt=exam_attempt,
                                                  question=question)
    answer_attempt.answers.add(correct_answers)

  def test_subject(self):
    """Unit test for Subject model."""

    subject = Subject.objects.get(name='Subject 1')

    self.assertEqual(str(subject), f'<Subject>: Subject 1')
    self.assertEqual(Subject.objects.count(), 1)

  def test_exam(self):
    """Unit test for Exam model."""

    exam = Exam.objects.get(name='Exam 1')

    self.assertEqual(str(exam), f'<Exam>: Exam 1')
    self.assertEqual(Exam.objects.count(), 1)

  def test_exam_attempt(self):
    """Unit test for ExamAttempt model."""

    exam_attempt = ExamAttempt.objects.get(exam=1)

    self.assertEqual(
        str(exam_attempt),
        f'This exam attempt was created on {exam_attempt.created} by {exam_attempt.user}'
    )
    self.assertEqual(ExamAttempt.objects.count(), 1)

  def test_answer_attempt(self):
    """Unit test for AnswerAttempt model."""

    answer_attempt = AnswerAttempt.objects.get(id=1)

    self.assertEqual(
        str(answer_attempt),
        f'This is an answer attempt #{answer_attempt.id} for an attempt #{answer_attempt.attempt.id}'
    )
    self.assertEqual(AnswerAttempt.objects.count(), 1)
