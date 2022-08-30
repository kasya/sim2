"""Tests for Question app views."""

import json
from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt
from apps.question.models import Answer, Question
from apps.question.serializers import QuestionSerializer
from apps.user.models import User


class QuestionViewTestCase(TestCase):
  """Test cases for question views."""

  client = Client()
  fixtures = [
      'answer.json', 'exam.json', 'exam_attempt.json', 'question.json',
      'question_category.json', 'subject.json', 'user.json'
  ]
  user_password = 'mypassword'

  def setUp(self):

    self.attempt = ExamAttempt.objects.get(id=1)
    self.exam = Exam.objects.get(id=1)
    self.question = Question.objects.get(id=1)
    self.user = User.objects.get(id=4)

  def test_api_get_question_anonymous(self):
    """Try to access page with anonymous user."""

    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': self.attempt.id}))
    self.assertEqual(response.status_code, 404)

  def test_api_get_question_unauthorized_user(self):
    """Try to login unauthorized user and access page."""

    user = User.objects.get(id=5)
    self.client.login(username=user.username, password=self.user_password)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': self.attempt.id}))
    self.assertEqual(response.status_code, 404)

  def test_api_get_question(self):
    """Check that method sends correct data to frontend."""

    self.client.login(username=self.user.username, password=self.user_password)
    with mock.patch('random.shuffle', return_value=lambda x: x):
      response = self.client.get(
          reverse('question_api',
                  kwargs={'attempt_id': self.attempt.id})).render()

      data = json.loads(response.content)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(QuestionSerializer(self.question).data, data)

  def test_api_get_question_no_more_questions(self):
    """
    Check that method returns status code 200
    when there's no more unanswered questions.
    """

    self.client.login(username=self.user.username, password=self.user_password)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': self.attempt.id}))

    self.assertEqual(response.status_code, 200)

  def test_api_post_question_anonymous(self):
    """Try to access page with anonymous user."""

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': self.attempt.id}),
                                data={'question_id': 1})

    self.assertEqual(response.status_code, 404)

  def test_api_post_question_404(self):
    """
    Check that method raise status code 404
    if required data is missing.
    """

    self.client.login(username=self.user.username, password=self.user_password)
    invalid_data = ({}, {'question_id': 1})

    for data in invalid_data:
      response = self.client.post(reverse(
          'question_api', kwargs={'attempt_id': self.attempt.id}),
                                  data=data)
      self.assertEqual(response.status_code, 404)

  def test_api_post_question(self):
    """Check that method creates Answer Attempt and saves answer to db."""

    correct_answer = Answer.objects.get(id=1)
    attempt = ExamAttempt.objects.create(user=self.user)
    attempt.exam.set([self.exam])

    self.client.login(username=self.user.username, password=self.user_password)

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [correct_answer.id],
                                    'question_id': self.question.id
                                })

    self.assertEqual(response.status_code, 201)
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertEqual(answer_attempt.answers.first().id, correct_answer.id)

  def test_api_post_update_answers(self):
    """Check that answer id in db changes when we change our answers."""

    attempt = ExamAttempt.objects.create(user=self.user)
    attempt.exam.set([self.exam])
    correct_answer = Answer.objects.get(id=1)
    wrong_answer = Answer.objects.get(id=2)

    self.client.login(username=self.user.username, password=self.user_password)

    self.client.post(reverse('question_api', kwargs={'attempt_id': attempt.id}),
                     data={
                         'answers': [correct_answer.id],
                         'question_id': self.question.id
                     })

    self.client.post(reverse('question_api', kwargs={'attempt_id': attempt.id}),
                     data={
                         'answers': [wrong_answer.id],
                         'question_id': self.question.id
                     })
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertIsNotNone(answer_attempt)
    self.assertEqual(answer_attempt.answers.first().id, wrong_answer.id)

  def test_get_attempt_question_answers_anonymous(self):
    """Check that method raise status code 404 for anonymous user."""

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': self.attempt.id,
                    'question_id': self.question.id
                }))
    self.assertEqual(response.status_code, 404)

  def test_get_attempt_wrong_question(self):
    """Check for case when question not in this attempt."""

    question = Question.objects.get(id=2)
    self.client.login(username=self.user.username, password=self.user_password)

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': self.attempt.id,
                    'question_id': question.id
                }))

    self.assertEqual(response.status_code, 404)

  def test_get_attempt_no_question(self):
    """Check for case when question does not exist in db."""

    self.client.login(username=self.user.username, password=self.user_password)

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': self.attempt.id,
                    'question_id': 10,
                }))

    self.assertEqual(response.status_code, 404)

  def test_get_api_attempt_question_answers(self):
    """Check that method send correct data to frontend."""

    correct_answer = Answer.objects.get(id=1)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.attempt,
                                                  question=self.question)
    answer_attempt.answers.add(correct_answer)

    self.client.login(username=self.user.username, password=self.user_password)
    with mock.patch('random.shuffle', return_value=lambda x: x):

      response = self.client.get(
          reverse('question_answers_api',
                  kwargs={
                      'attempt_id': self.attempt.id,
                      'question_id': self.question.id
                  }))

      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.data['answer_ids'], [correct_answer.id])
      self.assertEqual(response.data['question'],
                       QuestionSerializer(self.question).data)

  def test_get_question_flag_no_flags(self):
    """Check that method returns empty list when there's no flagged questions."""

    self.client.login(username=self.user.username, password=self.user_password)
    response = self.client.get(
        reverse('get_attempt', kwargs={'attempt_id': self.attempt.id}))

    self.assertEqual(response.data['flagged_questions'], [])

  def test_get_question_flag(self):
    """Check that method returns list of flagged questions."""

    self.client.login(username=self.user.username, password=self.user_password)
    self.attempt.flagged_questions.add(self.question)

    response = self.client.get(
        reverse('get_attempt', kwargs={'attempt_id': self.attempt.id}))

    self.assertEqual(response.data['flagged_questions'], [self.question.id])

  def test_post_question_flag_add(self):
    """Check that method adds flag from list of flagged questions."""

    self.client.login(username=self.user.username, password=self.user_password)

    response = self.client.post(
        reverse('question_toggle_flag',
                kwargs={
                    'attempt_id': self.attempt.id,
                    'question_id': self.question.id
                }))
    self.assertEqual(response.data['flagged_questions'], [self.question.id])

  def test_post_question_flag_remove(self):
    """Check that method removes flag from list of flagged questions."""

    self.client.login(username=self.user.username, password=self.user_password)
    self.attempt.flagged_questions.add(self.question)

    response = self.client.post(
        reverse('question_toggle_flag',
                kwargs={
                    'attempt_id': self.attempt.id,
                    'question_id': self.question.id
                }))
    self.assertEqual(response.data['flagged_questions'], [])

  def test_post_check_answer_wrong(self):

    attempt = ExamAttempt.objects.create(user=self.user)
    attempt.exam.set([self.exam])
    wrong_answer_id = [1, 2]

    self.client.login(username=self.user.username, password=self.user_password)

    response = self.client.post(reverse(
        'check_answer_api', kwargs={'question_id': self.question.id}),
                                data={
                                    'answer_ids': wrong_answer_id,
                                    'question_id': self.question.id
                                })

    self.assertEqual(response.data['result'], 'wrong')

  def test_post_check_answer_correct(self):

    attempt = ExamAttempt.objects.create(user=self.user)
    attempt.exam.set([self.exam])
    correct_answer_id = 1

    self.client.login(username=self.user.username, password=self.user_password)
    response = self.client.post(reverse(
        'check_answer_api', kwargs={'question_id': self.question.id}),
                                data={
                                    'answer_ids': [correct_answer_id],
                                    'question_id': self.question.id,
                                })
    self.assertEqual(response.data['result'], 'correct')
