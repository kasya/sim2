"""Tests for Exam app views."""
import json

from django.test import Client, TestCase
from django.urls import reverse

from rest_framework.response import Response

from apps.exam.models import Exam, ExamAttempt, Subject
from apps.exam.serializers import (ExamAttemptSerializer, ExamSerializer,
                                   SubjectSerializer)
from apps.question.models import Answer, Question, QuestionCategory
from apps.user.models import User


class ExamViewTestCase(TestCase):
  """Test cases for user views."""

  client = Client()
  username = 'John'
  password = 'password'
  exam_name = 'Exam 1'
  subject_name = 'Subject 1'

  def setUp(self):

    subject = Subject.objects.create(name=self.subject_name)
    exam = Exam.objects.create(name=self.exam_name, subject=subject)
    user = User.objects.create_user(username=self.username,
                                    password=self.password)
    question_category = QuestionCategory.objects.create(name='Category 1')
    question = Question.objects.create(text='Question 1',
                                       category=question_category,
                                       exam=exam)
    correct_answers = Answer.objects.create(text='Answer 1')
    wrong_answers = Answer.objects.create(text='Answer 2')
    question.correct_answers.add(correct_answers)
    question.wrong_answers.add(wrong_answers)

  def test_api_subject_list_get(self):
    """Check that method returns a list of all available subjects."""

    subject = Subject.objects.get(name=self.subject_name)
    response = self.client.get(reverse('subject_list')).render()
    # check that authentication works.
    self.assertEqual(response.status_code, 403)
    # login user and check again
    user = User.objects.get(username=self.username)
    self.client.login(username=user.username, password=self.password)
    response = self.client.get(reverse('subject_list')).render()
    data = json.loads(response.content)

    self.assertEqual(response.status_code, 200)
    self.assertEqual([SubjectSerializer(subject).data], data)

  def test_api_exam_list_get(self):
    """Check that method returns a list of all available exams."""

    exam = Exam.objects.get(name=self.exam_name)
    response = self.client.get(
        reverse('exam_list', kwargs={'subject_id': exam.subject.id})).render()
    # check that authentication works.
    self.assertEqual(response.status_code, 403)
    # login user and check again
    user = User.objects.get(username=self.username)
    self.client.login(username=user.username, password=self.password)
    response = self.client.get(
        reverse('exam_list', kwargs={'subject_id': exam.subject.id})).render()
    data = json.loads(response.content)

    self.assertEqual(response.status_code, 200)
    self.assertEqual([ExamSerializer(exam).data], data)

  def test_exam_intro_get(self):
    """Check that intro page for a given exam renders correctly."""

    user = User.objects.get(username=self.username)

    self.client.login(username=user.username, password=self.password)
    exam = Exam.objects.get(name=self.exam_name)

    response = self.client.get(
        reverse('exam_intro', kwargs={'exam_id': exam.id}))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(exam, response.context['exam'])

  def test_exam_intro_post(self):

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    # Try to access page without authentication.
    response = self.client.post(
        reverse('exam_intro', kwargs={'exam_id': exam.id}))

    self.assertEqual(response.status_code, 302)
    # self.assertRedirects(response, reverse('login'))

    # Check extra time addition to exam.
    self.client.login(username=user.username, password=self.password)
    user.requires_extra_time = True
    user.save()
    response = self.client.post(
        reverse('exam_intro', kwargs={'exam_id': exam.id}))
    exam_attempt = ExamAttempt.objects.get(user=user, exam=exam)
    self.assertEqual(exam_attempt.duration_minutes, exam.duration_minutes + 30)
    # Check question count for an exam attempt:
    self.assertEqual(exam_attempt.questions.all().count(),
                     exam.question_set.all().count())

    self.assertRedirects(
        response,
        reverse(
            'exam_page',
            kwargs={
                'exam_id': exam.id,
                'attempt_id': ExamAttempt.objects.get(user=user, exam=exam).id
            }))

  def test_exam_page_get(self):
    """Check that page renders with the right attempt_id."""

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    exam_attempt = ExamAttempt.objects.create(user=user, exam=exam)
    attempt = ExamAttempt.objects.get(exam=exam)

    response = self.client.get(
        reverse('exam_page',
                kwargs={
                    'exam_id': exam.id,
                    'attempt_id': exam_attempt.id
                }))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('exam/exam_attempt.html')
    self.assertEqual(exam_attempt, response.context['attempt'])
    self.assertEqual('http://127.0.0.1:8000/', response.context['api_url'])

  def test_exam_finish_get(self):
    """Check that finish page renders correctly and shows grade for the exam."""

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)
    self.client.login(username=user.username, password=self.password)

    exam_attempt = ExamAttempt.objects.create(user=user, exam=exam)
    attempt = ExamAttempt.objects.get(exam=exam)

    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': exam_attempt.id}))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('exam/finish.html')
    self.assertEqual(exam, response.context['exam'])
    self.assertEqual(exam_attempt.grade, response.context['grade'])

  def test_get_attempt(self):

    exam = Exam.objects.get(name=self.exam_name)
    user = User.objects.get(username=self.username)

    # Check case when user is not authorized.
    response = self.client.get(reverse('get_attempt', kwargs={'attempt_id': 1}))
    self.assertEqual(response.status_code, 403)
    # Check case when there's no attempt yet.
    self.client.login(username=user.username, password=self.password)
    response = self.client.get(reverse('get_attempt', kwargs={'attempt_id': 1}))
    self.assertEqual(response.status_code, 404)

    exam_attempt = ExamAttempt.objects.create(exam=exam, user=user)
    response = self.client.get(
        reverse('get_attempt', kwargs={'attempt_id': exam_attempt.id}))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data, ExamAttemptSerializer(exam_attempt).data)
