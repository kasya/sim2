"""Tests for Exam app models."""

from django.test import TestCase

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject
from apps.question.models import Answer, Question
from apps.user.models import User


class ExamModelTestCase(TestCase):
  """Test cases for exam models."""

  fixtures = [
      'answer.json', 'answer_attempt.json', 'exam.json', 'exam_attempt.json',
      'question.json', 'question_category.json', 'subject.json', 'user.json'
  ]

  def setUp(self):

    self.subject = Subject.objects.get(id=1)
    self.exam = Exam.objects.get(id=2)
    self.user = User.objects.get(id=4)
    self.exam_attempt = ExamAttempt.objects.get(id=2)
    self.correct_answer1 = Answer.objects.get(id=1)
    self.correct_answer2 = Answer.objects.get(id=4)
    self.wrong_answers = Answer.objects.get(id=2)
    self.question = Question.objects.get(id=2)

    self.answer_attempt = AnswerAttempt.objects.get(id=3)
    self.question1 = Question.objects.get(id=3)

  def test_subject(self):
    """Unit test for Subject model."""

    self.assertEqual(str(self.subject), '<Subject>: English, id# 1')

  def test_exam(self):
    """Unit test for Exam model."""

    self.assertEqual(str(self.exam), '<Exam>: Exam 2, id# 2')

  def test_exam_attempt(self):
    """Unit test for ExamAttempt model."""

    self.assertEqual(str(self.exam_attempt), '<ExamAttempt>: id# 2')

  def test_answer_attempt(self):
    """Unit test for AnswerAttempt model."""

    self.assertEqual(str(self.answer_attempt), '<AnswerAttempt>: id# 3')

  def test_calculate_grade_no_answers(self):
    """Check correct grading of the exam attempt."""

    exam_attempt = ExamAttempt.objects.get(id=3)
    self.assertEqual(exam_attempt.calculate_grade(), 0)

  def test_calculate_grade_multiple_choice(self):
    """Check grading for questions with single answer."""

    self.exam_attempt.questions.add(self.question)
    self.exam_attempt.grade = 0
    self.exam_attempt.save()

    self.answer_attempt.answers.set([self.correct_answer1])
    self.assertEqual(self.exam_attempt.calculate_grade(), 100)

  def test_calculate_grade_multiple_select(self):
    """Check grading for questions with multiple select answers."""

    self.exam_attempt.questions.set([self.question1])
    self.answer_attempt.question = self.question1
    self.answer_attempt.save()
    self.answer_attempt.answers.set(
        [self.correct_answer1, self.correct_answer2])

    self.assertEqual(self.exam_attempt.calculate_grade(), 100)

  def test_calculate_grade_wrong_answer(self):
    """Add wrong answer. Should decrease the grade."""

    self.exam_attempt.questions.set([self.question1])
    self.answer_attempt.question = self.question1
    self.answer_attempt.save()
    self.answer_attempt.answers.set(
        [self.correct_answer1, self.correct_answer2])

    self.answer_attempt.answers.add(self.wrong_answers)

    self.assertEqual(self.exam_attempt.calculate_grade(), 0)

  def test_exam_attempt_passed(self):
    """Check that method correctly verifies if exam has been passed."""

    self.exam.passing_grade = 80
    self.exam.save()

    passing_values = (80, 100)
    failing_values = (0, 50, 75)

    for value in passing_values:
      self.exam_attempt.grade = value
      self.assertTrue(self.exam_attempt.passed)

    for value in failing_values:
      self.exam_attempt.grade = value
      self.assertFalse(self.exam_attempt.passed)
