"""Tests for Question app views."""

import json
from unittest import mock

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
  extra_user_username = 'Jane'
  extra_user_password = 'multipass'
  exam_name = 'Exam 1'
  subject_name = 'Subject 1'
  question_text = 'Question 1'

  def setUp(self):

    question_category = QuestionCategory.objects.create(name='Category 1')
    subject = Subject.objects.create(name=self.subject_name)
    exam = Exam.objects.create(name=self.exam_name, subject=subject)
    exam1 = Exam.objects.create(name='Exam 2', subject=subject)

    correct_answers = Answer.objects.create(text='Answer 1')
    wrong_answers = Answer.objects.create(text='Answer 2')
    question = Question.objects.create(text=self.question_text,
                                       category=question_category,
                                       exam=exam)
    self.question2 = Question.objects.create(text='Question 2',
                                             category=question_category,
                                             exam=exam1)
    question.correct_answers.add(correct_answers)
    question.wrong_answers.add(wrong_answers)
    User.objects.create_user(username=self.username, password=self.password)
    User.objects.create_user(username=self.extra_user_username,
                             password=self.extra_user_password)

  def test_api_get_question(self):
    """Check that method send the correct question to frontend."""

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    extra_user = User.objects.get(username=self.extra_user_username)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)
    question = Question.objects.get(text=self.question_text)
    attempt.questions.add(question)

    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id}))
    self.assertEqual(response.status_code, 404)

    # try to login different user and access page
    self.client.login(username=extra_user.username,
                      password=self.extra_user_password)
    response = self.client.get(
        reverse('question_api', kwargs={'attempt_id': attempt.id}))
    self.assertEqual(response.status_code, 404)

    self.client.login(username=user.username, password=self.password)

    with mock.patch('random.shuffle', return_value=lambda x: x):
      response = self.client.get(
          reverse('question_api', kwargs={'attempt_id': attempt.id})).render()
      data = json.loads(response.content)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(QuestionSerializer(question).data, data)

  def test_api_post_question(self):
    """
    Check that method get correct data 
    from frontend and save it to database.
    """

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)
    question = Question.objects.get(text=self.question_text)
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

    expected_result = wrong_answer

    response = self.client.post(reverse('question_api',
                                        kwargs={'attempt_id': attempt.id}),
                                data={
                                    'answers': [wrong_answer.id],
                                    'question_id': 1
                                }).render()
    answer_attempt = AnswerAttempt.objects.get(attempt=attempt.id)
    self.assertIsNotNone(answer_attempt)
    self.assertEqual(answer_attempt.answers.first().id, expected_result.id)

  def test_get_attempt_question_answers(self):
    """Check that method return correct question and answers to it."""

    exam = Exam.objects.get(name=self.exam_name)
    subject = Subject.objects.get(name=self.subject_name)
    user = User.objects.get(username=self.username)
    attempt = ExamAttempt.objects.create(user=user, exam=exam)
    question = Question.objects.get(text=self.question_text)
    answer_attempt = AnswerAttempt.objects.create(attempt=attempt,
                                                  question=question)
    correct_answer = Answer.objects.get(text='Answer 1')

    # Check for anonymous user.
    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': attempt.id,
                    'question_id': question.id
                }))
    self.assertEqual(response.status_code, 404)

    # Check for case when question not in this attempt.
    self.client.login(username=user.username, password=self.password)

    response = self.client.get(
        reverse('question_answers_api',
                kwargs={
                    'attempt_id': attempt.id,
                    'question_id': self.question2.id
                }))

    self.assertEqual(response.status_code, 404)

    attempt.questions.add(question)
    answer_attempt.answers.add(correct_answer)
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
