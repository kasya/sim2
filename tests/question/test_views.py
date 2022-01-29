"""Tests for Question app views."""

import json

from django.test import Client, TestCase
from django.urls import reverse

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject
from apps.question.models import Answer, Question, QuestionCategory
from apps.question.serializers import QuestionSerializer
from apps.user.models import User


class UserViewTestCase(TestCase):
  """Test cases for question views."""

  client = Client()
  username = 'John'
  password = 'password'
  exam_name = 'Exam 1'
  subject_name = 'Subject 1'

  def setUp(self):

    question_category = QuestionCategory.objects.create(name='Category 1')
    subject = Subject.objects.create(name=self.subject_name)
    exam = Exam.objects.create(name=self.exam_name, subject=subject)
    correct_answers = Answer.objects.create(text='Answer 1')
    wrong_answers = Answer.objects.create(text='Answer 2')
    question = Question.objects.create(text='Question 1',
                                       category=question_category,
                                       exam=exam)
    question.correct_answers.add(correct_answers)
    question.wrong_answers.add(wrong_answers)
    user = User.objects.create_user(username=self.username,
                                    password=self.password)

  def test_api_get_question(self):
    """Check that method send the correct question to frontend."""

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)
    question = Question.objects.get(text='Question 1')
    attempt.questions.add(question)

    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id})).render()
    self.assertEqual(response.status_code, 403)

    self.client.login(username=user.username, password=self.password)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id})).render()
    data = json.loads(response.content)

    self.assertEqual(response.status_code, 200)

    self.assertEqual(json.dumps(QuestionSerializer(question).data), data)

  def test_api_post_question(self):
    """
    Check that method get correct data 
    from frontend and save it to database.
    """

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)
    question = Question.objects.get(text='Question 1')
    attempt.questions.add(question)
    correct_answer = Answer.objects.get(text='Answer 1')
    wrong_answer = Answer.objects.get(text='Answer 2')

    self.client.login(username=user.username, password=self.password)

    # try to send data in without answer ids
    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'question_id': 1
                                }).render()

    self.assertEqual(response.status_code, 404)

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [correct_answer.id],
                                    'question_id': 1
                                }).render()

    self.assertEqual(response.status_code, 201)
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertIsNotNone(answer_attempt)
    self.assertEqual(answer_attempt.answers.first().id, correct_answer.id)
    # Check that answer id in db changes when we change our answers.

    expected_result = [wrong_answer]

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [wrong_answer.id],
                                    'question_id': 1
                                }).render()
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertIsNotNone(answer_attempt)
    self.assertEqual(answer_attempt.answers.first().id, wrong_answer.id)
