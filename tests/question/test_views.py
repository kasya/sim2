"""Tests for Question app views."""

import json
from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject
from apps.question.models import Answer, Question, QuestionCategory
from apps.question.serializers import QuestionSerializer
from apps.user.models import User


class QuestionViewTestCase(TestCase):
  """Test cases for question views."""

  client = Client()
  fixtures = [
      'exam_attempt.json', 'user.json', 'exam.json', 'subject.json',
      'question.json', 'question_category.json', 'answer.json'
  ]
  user_password = 'mypassword'

  def test_api_get_question_anonymous(self):
    """Try to access page with anonymous user."""

    attempt = ExamAttempt.objects.get(id=1)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id}))
    self.assertEqual(response.status_code, 404)

  def test_api_get_question_wrong_user(self):
    """Try to login wrong user and access page."""
    attempt = ExamAttempt.objects.get(id=1)
    user = User.objects.get(id=5)

    self.client.login(username=user.username, password=self.user_password)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id}))
    self.assertEqual(response.status_code, 404)

  def test_api_get_question(self):
    """Check that method send correct data to frontend."""

    user = User.objects.get(id=4)
    exam = Exam.objects.get(id=1)
    attempt = ExamAttempt.objects.get(id=1)
    question = Question.objects.get(id=1)

    self.client.login(username=user.username, password=self.user_password)
    with mock.patch('random.shuffle', return_value=lambda x: x):
      response = self.client.get(
          reverse('question_api', kwargs={'attempt_id': attempt.id})).render()

      data = json.loads(response.content)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(QuestionSerializer(question).data, data)
      AnswerAttempt.objects.create(attempt=attempt, question=question)

  def test_api_get_question_no_more_questions(self):
    """
    Check that method returns status code 200 
    when there's no more unanswered questions.
    """

    attempt = ExamAttempt.objects.get(id=1)
    user = User.objects.get(id=4)

    self.client.login(username=user.username, password=self.user_password)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id}))

    self.assertEqual(response.status_code, 200)

  def test_api_post_question_anonymous(self):
    """Try to access page with anonymous user."""

    attempt = ExamAttempt.objects.get(id=1)
    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={'question_id': 1})

    self.assertEqual(response.status_code, 404)

  def test_api_post_question_404(self):
    """
    Check that method raise status code 404
    if required data is missing.
    """

    attempt = ExamAttempt.objects.get(id=1)
    user = User.objects.get(id=4)
    self.client.login(username=user.username, password=self.user_password)
    required_data = ({}, {'question_id': 1})

    for data in required_data:
      response = self.client.post(reverse('question_api',
                                          kwargs={'attempt_id': attempt.id}),
                                  data=data)
      self.assertEqual(response.status_code, 404)

  def test_api_post_question(self):
    """Check that method creates Answer Attempt ans saves answer to db."""

    question = Question.objects.get(id=1)
    correct_answer = Answer.objects.get(id=1)
    user = User.objects.get(id=4)
    exam = Exam.objects.get(id=1)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)

    self.client.login(username=user.username, password=self.user_password)

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [correct_answer.id],
                                    'question_id': question.id
                                })

    self.assertEqual(response.status_code, 201)
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertEqual(answer_attempt.answers.first().id, correct_answer.id)

  def test_api_post_update_answers(self):
    """Check that answer id in db changes when we change our answers."""

    question = Question.objects.get(id=1)
    correct_answer = Answer.objects.get(id=1)
    wrong_answer = Answer.objects.get(id=2)
    user = User.objects.get(id=4)
    exam = Exam.objects.get(id=1)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)

    self.client.login(username=user.username, password=self.user_password)

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [correct_answer.id],
                                    'question_id': question.id
                                })

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [wrong_answer.id],
                                    'question_id': question.id
                                })
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertIsNotNone(answer_attempt)
    self.assertEqual(answer_attempt.answers.first().id, wrong_answer.id)

  def test_get_attempt_question_answers_anonymous(self):
    """Check that method raise status code 404 for anonymous user."""

    attempt = ExamAttempt.objects.get(id=1)
    question = Question.objects.get(id=1)

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': attempt.id,
                    'question_id': question.id
                }))
    self.assertEqual(response.status_code, 404)

  def test_get_attempt_wrong_question(self):
    """Check for case when question not in this attempt."""

    attempt = ExamAttempt.objects.get(id=1)
    question = Question.objects.get(id=2)
    user = User.objects.get(id=4)
    self.client.login(username=user.username, password=self.user_password)

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': attempt.id,
                    'question_id': question.id
                }))

    self.assertEqual(response.status_code, 404)

  def test_get_attempt_no_question(self):
    """Check for case when question does not exist in db."""

    attempt = ExamAttempt.objects.get(id=1)
    user = User.objects.get(id=4)
    self.client.login(username=user.username, password=self.user_password)

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': attempt.id,
                    'question_id': 10,
                }))

    self.assertEqual(response.status_code, 404)

  def test_get_api_attempt_question_answers(self):
    """Check that method send correct data to frontend."""

    attempt = ExamAttempt.objects.get(id=1)
    user = User.objects.get(id=4)
    question = Question.objects.get(id=1)
    correct_answer = Answer.objects.get(id=1)
    answer_attempt = AnswerAttempt.objects.create(attempt=attempt,
                                                  question=question)
    answer_attempt.answers.add(correct_answer)

    self.client.login(username=user.username, password=self.user_password)
    with mock.patch('random.shuffle', return_value=lambda x: x):

      response = self.client.get(
          reverse('question_answers_api',
                  kwargs={
                      'attempt_id': attempt.id,
                      'question_id': question.id
                  }))

      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.data['answer_ids'], [correct_answer.id])
      self.assertEqual(response.data['question'],
                       QuestionSerializer(question).data)
