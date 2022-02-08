"""Tests for Exam app views."""
import json

from django.test import Client, TestCase
from django.urls import reverse

from rest_framework.response import Response

from apps.exam.models import Exam, ExamAttempt, Subject, AnswerAttempt
from apps.exam.serializers import (ExamAttemptSerializer, ExamSerializer,
                                   SubjectSerializer)
from apps.question.models import Answer, Question, QuestionCategory
from apps.user.models import User


class ExamViewTestCase(TestCase):
  """Test cases for user views."""

  client = Client()
  fixtures = [
      'answer.json', 'exam.json', 'exam_attempt.json', 'question.json',
      'question_category.json', 'subject.json', 'user.json'
  ]
  password = 'mypassword'

  def setUp(self):

    self.answer = Answer.objects.get(id=1)
    self.attempt = ExamAttempt.objects.get(id=1)
    self.exam = Exam.objects.get(id=1)
    self.question = Question.objects.get(id=1)
    self.subject = Subject.objects.get(id=1)
    self.user = User.objects.get(id=4)

  def test_api_subject_list_get_unauthorized(self):
    """Check access for unauthorized user."""

    response = self.client.get(reverse('subject_list')).render()
    self.assertEqual(response.status_code, 403)

  def test_api_subject_list_get(self):
    """Check that method returns a list of all available subjects."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(reverse('subject_list')).render()
    data = json.loads(response.content)
    subjects = [
        SubjectSerializer(subject).data for subject in Subject.objects.all()
    ]
    self.assertEqual(response.status_code, 200)
    self.assertEqual(subjects, data)

  def test_api_exam_list_get_unauthorized(self):
    """Check access for unauthorized user."""

    response = self.client.get(
        reverse('exam_list',
                kwargs={'subject_id': self.exam.subject.id})).render()
    self.assertEqual(response.status_code, 403)

  def test_api_exam_list_get(self):
    """Check that method returns a list of all available exams."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_list',
                kwargs={'subject_id': self.exam.subject.id})).render()
    data = json.loads(response.content)
    exams = [
        ExamSerializer(exam).data
        for exam in Exam.objects.filter(subject=self.subject)
    ]
    self.assertEqual(response.status_code, 200)
    self.assertEqual(exams, data)

  def test_exam_intro_get_unauthorized(self):
    """Check access for unauthorized user."""

    response = self.client.get(
        reverse('exam_intro', kwargs={'exam_id': self.exam.id}))

    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
        response,
        f'{reverse("login")}?next={reverse("exam_intro", kwargs={"exam_id": self.exam.id})}'
    )

  def test_exam_intro_get(self):
    """Check that intro page for a given exam renders correctly."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_intro', kwargs={'exam_id': self.exam.id}))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(self.exam, response.context['exam'])

  def test_exam_intro_post_unauthorized(self):
    """Check access for unauthorized user."""

    response = self.client.post(
        reverse('exam_intro', kwargs={'exam_id': self.exam.id}))

    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
        response,
        f'{reverse("login")}?next={reverse("exam_intro", kwargs={"exam_id": self.exam.id})}'
    )

  def test_exam_intro_post_extra_time(self):
    """Check extra time addition to exam."""

    self.client.login(username=self.user.username, password=self.password)
    self.user.requires_extra_time = True
    self.user.save()

    response = self.client.post(
        reverse('exam_intro', kwargs={'exam_id': self.exam.id}))
    exam_attempt = ExamAttempt.objects.filter(user=self.user,
                                              exam=self.exam).last()

    self.assertEqual(exam_attempt.duration_minutes,
                     self.exam.duration_minutes + 30)

  def test_exam_intro_post(self):
    """
    Check question count for an exam attempt 
    and that method redirects to exam page.
    """

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.post(
        reverse('exam_intro', kwargs={'exam_id': self.exam.id}))
    exam_attempt = ExamAttempt.objects.filter(user=self.user,
                                              exam=self.exam).last()
    self.assertEqual(exam_attempt.questions.count(),
                     self.exam.questions.count())

    self.assertRedirects(
        response,
        reverse('exam_page',
                kwargs={
                    'exam_id':
                        self.exam.id,
                    'attempt_id':
                        ExamAttempt.objects.filter(user=self.user,
                                                   exam=self.exam).last().id
                }))

  def test_exam_page_get(self):
    """Check that method renders correctly."""

    response = self.client.get(
        reverse('exam_page',
                kwargs={
                    'exam_id': self.exam.id,
                    'attempt_id': self.attempt.id
                }))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('exam/exam_attempt.html')

  def test_exam_page_get_context(self):
    """Check that method returns correct context data."""

    response = self.client.get(
        reverse('exam_page',
                kwargs={
                    'exam_id': self.exam.id,
                    'attempt_id': self.attempt.id
                }))
    self.assertEqual(self.attempt, response.context['attempt'])
    self.assertEqual('http://127.0.0.1:8000/', response.context['api_url'])

  def test_exam_finish_get_unauthorized_user(self):
    """Check access for unauthorized user."""

    user = User.objects.get(id=5)
    self.client.login(username=user.username, password=self.password)
    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.attempt.id}))
    self.assertEqual(response.status_code, 404)

  def test_exam_finish_get_not_all_questions(self):
    """Check that method returns 404 if exam is not finished."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.attempt.id}))
    self.assertEqual(response.status_code, 404)
    self.assertTemplateUsed('exam/finish.html')

  def test_exam_finish_get(self):
    """Check that finish page renders correctly."""

    self.client.login(username=self.user.username, password=self.password)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.attempt,
                                                  question=self.question)
    answer_attempt.answers.add(self.answer)
    answer_attempt.save()

    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.attempt.id}))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('exam/finish.html')

  def test_exam_finish_get_context(self):
    """Check that method returns correct context."""

    self.client.login(username=self.user.username, password=self.password)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.attempt,
                                                  question=self.question)
    answer_attempt.answers.add(self.answer)
    answer_attempt.save()

    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.attempt.id}))

    self.assertEqual(response.context['exam'], self.exam)
    self.assertEqual(response.context['grade'], self.attempt.grade)

  def test_get_attempt_unauthorized(self):
    """Check access for unauthorized user."""

    response = self.client.get(reverse('get_attempt', kwargs={'attempt_id': 1}))
    self.assertEqual(response.status_code, 403)

  def test_get_attempt_no_attempt(self):
    """Check case when there's no such attempt in db."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(reverse('get_attempt',
                                       kwargs={'attempt_id': 10}))
    self.assertEqual(response.status_code, 404)

  def test_get_attempt(self):
    """Check that method returns correct exam attempt."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('get_attempt', kwargs={'attempt_id': self.attempt.id}))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data, ExamAttemptSerializer(self.attempt).data)
