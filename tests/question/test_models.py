"""Tests for Question app models."""

from django.test import TestCase

from apps.exam.models import Exam, Subject
from apps.question.models import Answer, Question, QuestionCategory


class QuestionModelTestCase(TestCase):
  """Test cases for Question models."""

  fixtures = [
      'exam_attempt.json', 'user.json', 'exam.json', 'subject.json',
      'question.json', 'question_category.json', 'answer.json'
  ]

  def test_answer_model(self):
    """Unit test for answer model."""

    answer = Answer.objects.get(id=1)

    self.assertEqual(str(answer), f'<Answer>: Correct!, id# 1')

  def test_question_model(self):
    """Unit test for question model."""

    question = Question.objects.get(id=1)

    self.assertEqual(str(question), f'<Question>: Question 1, id# 1:')

  def test_question_category(self):
    """Unit test for question category model."""

    category = QuestionCategory.objects.get(name="Category 1")

    self.assertEqual(str(category), f'<Category>: Category 1, id# 1')
