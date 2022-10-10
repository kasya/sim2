"""Tests for Question app models."""

from django.test import TestCase

from apps.question.models import Answer, Question, QuestionCategory


class QuestionModelTestCase(TestCase):
    """Test cases for Question models."""

    fixtures = [
        "answer.json",
        "exam.json",
        "exam_attempt.json",
        "question.json",
        "question_category.json",
        "subject.json",
        "user.json",
    ]

    def test_answer_model(self):
        """Unit test for answer model."""

        answer = Answer.objects.get(id=1)

        self.assertEqual(str(answer), "<Answer>: Correct!, id# 1")

    def test_question_model(self):
        """Unit test for question model."""

        question = Question.objects.get(id=1)

        self.assertEqual(str(question), "<Question>: Question 1, id# 1:")

    def test_question_category(self):
        """Unit test for question category model."""

        category = QuestionCategory.objects.get(name="Category 1")

        self.assertEqual(str(category), "<Category>: Category 1, id# 1")
