"""Tests for Exam app models."""

from django.test import TestCase

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject
from apps.question.models import Answer, Question, QuestionCategory
from apps.user.models import User


class ExamModelTestCase(TestCase):
  """Test cases for exam models."""

  username = 'John'
  password = 'password'
  exam_name = 'Exam 1'

  def setUp(self):

    subject = Subject.objects.create(name='Subject 1')
    exam = Exam.objects.create(name='Exam 1', subject=subject)
    user = User.objects.create_user(username='John', password='password')
    exam_attempt = ExamAttempt.objects.create(user=user, exam=exam)
    correct_answer1 = Answer.objects.create(text='Answer 1')
    correct_answer2 = Answer.objects.create(text='Answer 2')
    wrong_answers = Answer.objects.create(text='Answer 3')
    question_category = QuestionCategory.objects.create(name='Category 1')
    question = Question.objects.create(category=question_category,
                                       text='Question 1',
                                       exam=exam)
    question.correct_answers.add(correct_answer1)
    question.wrong_answers.add(wrong_answers)

    answer_attempt = AnswerAttempt.objects.create(attempt=exam_attempt,
                                                  question=question)
    question1 = Question.objects.create(category=question_category,
                                        text='Question 2',
                                        exam=exam)
    question1.correct_answers.add(correct_answer1, correct_answer2)
    question1.wrong_answers.add(wrong_answers)

  def test_subject(self):
    """Unit test for Subject model."""

    subject = Subject.objects.get(name='Subject 1')

    self.assertEqual(str(subject),
                     f'<Subject>: {subject.name}, id# {subject.id}')
    self.assertEqual(Subject.objects.count(), 1)

  def test_exam(self):
    """Unit test for Exam model."""

    exam = Exam.objects.get(name=self.exam_name)

    self.assertEqual(str(exam), f'<Exam>: {exam.name}, id# {exam.id}')
    self.assertEqual(Exam.objects.count(), 1)

  def test_exam_attempt(self):
    """Unit test for ExamAttempt model."""

    exam_attempt = ExamAttempt.objects.get(exam=1)

    self.assertEqual(str(exam_attempt), f'<ExamAttempt>: id# {exam_attempt.id}')
    self.assertEqual(ExamAttempt.objects.count(), 1)

  def test_answer_attempt(self):
    """Unit test for AnswerAttempt model."""

    answer_attempt = AnswerAttempt.objects.get(id=1)

    self.assertEqual(str(answer_attempt),
                     f'<AnswerAttempt>: id# {answer_attempt.id}')
    self.assertEqual(AnswerAttempt.objects.count(), 1)

  def test_calculate_grade(self):
    """Check correct grading of the exam attempt."""

    user = User.objects.get(username=self.username)
    exam = Exam.objects.get(name=self.exam_name)
    question = Question.objects.get(text='Question 1', exam=exam)
    exam_attempt = ExamAttempt.objects.get(user=user, exam=exam)
    self.assertEqual(exam_attempt.calculate_grade(), 0)

    # Check grading for questions with single answer
    exam_attempt.questions.add(question)
    answer_attempt = AnswerAttempt.objects.get(attempt=exam_attempt,
                                               question=question)
    correct_answer1 = Answer.objects.get(text='Answer 1')
    answer_attempt.answers.add(correct_answer1)

    self.assertEqual(exam_attempt.calculate_grade(), 100)

    # Now add questions with multiple select answers
    question1 = Question.objects.get(text='Question 2', exam=exam)
    exam_attempt.questions.add(question1)

    answer_attempt2 = AnswerAttempt.objects.create(question=question1,
                                                   attempt=exam_attempt)
    correct_answer2 = Answer.objects.get(text='Answer 2')
    answer_attempt2.answers.add(correct_answer1, correct_answer2)

    self.assertEqual(exam_attempt.calculate_grade(), 100)

    # Add wrong answer. Should decrease the grade
    wrong_answer = Answer.objects.get(text='Answer 3')
    answer_attempt2.answers.add(wrong_answer)

    self.assertEqual(exam_attempt.calculate_grade(), 50)
