"""Tests for Question app models."""

from apps.exam.models import Exam, Subject
from apps.question.models import Answer, Question, QuestionCategory
from django.test import TestCase


class QuestionModelTestCase(TestCase):
  """Test cases for Question models."""

  def setUp(self):

    question_category = QuestionCategory.objects.create(name='Category 1')
    subject = Subject.objects.create(name='Subject 1')
    exam = Exam.objects.create(name='Exam 1', subject=subject)
    correct_answers = Answer.objects.create(text='Answer 1')
    wrong_answers = Answer.objects.create(text='Answer 2')
    question = Question.objects.create(text='Question 1',
                                       category=question_category,
                                       exam=exam)
    question.correct_answers.add(correct_answers)
    question.wrong_answers.add(wrong_answers)

  def test_answer_model(self):
    """Unit test for answer model."""

    answer = Answer.objects.get(text='Answer 1')

    self.assertEqual(str(answer), f'<Answer>: {answer.text}, id#{answer.id}')

  def test_question_model(self):
    """Unit test for question model."""

    question = Question.objects.get(text="Question 1")

    self.assertEqual(str(question),
                     f'<Question>: {question.text}, id#{question.id}:')
    self.assertEqual(Question.objects.count(), 1)

  def test_question_category(self):
    """Unit test for question category model."""

    category = QuestionCategory.objects.get(name="Category 1")

    self.assertEqual(str(category),
                     f'<Category>: {category.name}, id#{category.id}')
    self.assertEqual(QuestionCategory.objects.count(), 1)
