"""Tests for Exam app views."""

from django.test import Client, TestCase
from django.urls import reverse

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject
from apps.exam.serializers import (ExamAttemptSerializer, ExamSerializer,
                                   SubjectSerializer)
from apps.question.models import Answer, Question
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
    self.exam_attempt = ExamAttempt.objects.get(id=1)
    self.subject_attempt = ExamAttempt.objects.get(id=2)
    self.exam = Exam.objects.get(id=1)
    self.question = Question.objects.get(id=1)
    self.subject = Subject.objects.get(id=1)
    self.user = User.objects.get(id=4)

  def test_api_subject_list_get_unauthenticated(self):
    """Check access denied for unauthenticated user."""

    response = self.client.get(reverse('subject_list')).render()
    self.assertEqual(response.status_code, 403)

  def test_api_subject_list_get(self):
    """Check that method returns a list of all available subjects."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(reverse('subject_list'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
        SubjectSerializer(Subject.objects.all(), many=True).data, response.data)

  def test_api_exam_list_get_unauthenticated(self):
    """Check access denied for unauthenticated user."""

    response = self.client.get(
        reverse('exam_list',
                kwargs={'subject_id': self.exam.subject.id})).render()
    self.assertEqual(response.status_code, 403)

  def test_api_exam_list_get(self):
    """Check that method returns a list of all available exams."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_list', kwargs={'subject_id': self.exam.subject.id}))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(
        ExamSerializer(Exam.objects.filter(subject=self.exam.subject),
                       many=True).data, response.data)

  def test_exam_intro_get_unauthenticated(self):
    """Check access denied for unauthenticated user."""

    response = self.client.get(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.PRACTICE_MODE,
                }))

    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
        response,
        f'{reverse("login")}?next={reverse("exam_intro", kwargs={"exam_id": self.exam.id, "exam_mode": "practice"})}'
    )

  def test_practice_intro_get(self):
    """Check that intro page for practice renders correctly."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.PRACTICE_MODE,
                }))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(self.exam, response.context['exam'])
    self.assertEqual(ExamAttempt.PRACTICE_MODE, response.context['exam_mode'])
    self.assertInHTML(
        f'<p>You chose to practice {self.subject.name} {self.exam.name}.</p>',
        response.content.decode('utf-8'))

  def test_exam_intro_get(self):
    """Check that intro page for a given exam renders correctly."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.EXAM_MODE,
                }))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(self.exam, response.context['exam'])
    self.assertEqual('exam', response.context['exam_mode'])
    self.assertInHTML(
        f'<p>You chose {self.exam.subject.name} {self.exam.name} as your exam.</p>',
        response.content.decode('utf-8'))

  def test_subject_attempt_intro_get(self):
    """Check that intro page for a given subject exam attempt renders correctly."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_intro',
                kwargs={
                    'subject_id': self.subject.id,
                    'exam_mode': ExamAttempt.EXAM_MODE,
                }))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(Subject.objects.get(id=self.subject.id),
                     response.context['subject'])
    self.assertEqual('exam', response.context['exam_mode'])
    self.assertInHTML(f'<p>You chose {self.subject.name} as your exam.</p>',
                      response.content.decode('utf-8'))

  def test_exam_intro_post_unauthenticated(self):
    """Check access denied for unauthenticated user."""

    response = self.client.post(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.PRACTICE_MODE,
                }))

    self.assertEqual(response.status_code, 302)
    self.assertRedirects(
        response, f'{reverse("login")}?next='
        f'{reverse("exam_intro", kwargs={"exam_id": self.exam.id, "exam_mode": "practice"})}'
    )

  def test_exam_intro_post_extra_time(self):
    """Check extra time addition to exam."""

    self.client.login(username=self.user.username, password=self.password)
    self.user.required_extra_time = 30
    self.user.save()

    self.client.post(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.PRACTICE_MODE,
                }))
    exam_attempt = ExamAttempt.objects.filter(user=self.user,
                                              exam=self.exam).last()
    self.assertEqual(exam_attempt.duration_minutes,
                     self.exam.duration_minutes + self.user.required_extra_time)

  def test_subject_attempt_practice_mode_intro_post(self):
    """
    Check intro page for subject exam attempt in practice mode 
    and that method redirects to exam page.
    """

    self.client.login(username=self.user.username, password=self.password)
    self.user.required_extra_time = 30
    self.user.save()

    response = self.client.post(
        reverse('exam_intro',
                kwargs={
                    'subject_id': self.subject.id,
                    'exam_mode': ExamAttempt.PRACTICE_MODE,
                }))
    exam_attempt = ExamAttempt.objects.filter(
        user=self.user, mode=ExamAttempt.PRACTICE_MODE).last()
    self.assertEqual(exam_attempt.duration_minutes,
                     self.exam.duration_minutes + self.user.required_extra_time)
    self.assertRedirects(
        response,
        reverse('exam_page',
                kwargs={
                    'attempt_id':
                        ExamAttempt.objects.filter(user=self.user).last().id
                }))

  def test_subject_attempt_exam_mode_intro_post(self):
    """
    Check intro post for subject exam attempt in exam mode
    and that method redirects to exam page.
    """

    self.client.login(username=self.user.username, password=self.password)
    subject_exams = Exam.objects.filter(subject=self.subject)
    subject_questions = subject_exams.values_list('id', flat=True).count()

    response = self.client.post(
        reverse('exam_intro',
                kwargs={
                    'subject_id': self.subject.id,
                    'exam_mode': ExamAttempt.EXAM_MODE,
                }))
    exam_attempt = ExamAttempt.objects.filter(
        user=self.user, mode=ExamAttempt.EXAM_MODE).last()
    self.assertEqual(exam_attempt.questions.count(), subject_questions)
    self.assertEqual(exam_attempt.mode, 'exam')

    self.assertRedirects(
        response,
        reverse('exam_page',
                kwargs={
                    'attempt_id':
                        ExamAttempt.objects.filter(user=self.user,
                                                   exam=self.exam).last().id
                }))

  def test_exam_attempt_practice_mode_intro_post(self):
    """
    Check question count for a practice attempt
    and that method redirects to exam page.
    """

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.post(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.PRACTICE_MODE,
                }))
    exam_attempt = ExamAttempt.objects.filter(user=self.user,
                                              exam=self.exam).last()
    self.assertEqual(exam_attempt.questions.count(),
                     self.exam.questions.count())
    self.assertEqual(exam_attempt.mode, ExamAttempt.PRACTICE_MODE)

    self.assertRedirects(
        response,
        reverse('exam_page',
                kwargs={
                    'attempt_id':
                        ExamAttempt.objects.filter(user=self.user,
                                                   exam=self.exam).last().id
                }))

  def test_exam_attempt_exam_mode_intro_post(self):
    """
    Check question count for a practice attempt
    and that method redirects to exam page.
    """

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.post(
        reverse('exam_intro',
                kwargs={
                    'exam_id': self.exam.id,
                    'exam_mode': ExamAttempt.EXAM_MODE,
                }))
    exam_attempt = ExamAttempt.objects.filter(user=self.user,
                                              exam=self.exam).last()
    self.assertEqual(exam_attempt.questions.count(),
                     self.exam.questions.count())
    self.assertEqual(exam_attempt.mode, ExamAttempt.EXAM_MODE)

    self.assertRedirects(
        response,
        reverse('exam_page',
                kwargs={
                    'attempt_id':
                        ExamAttempt.objects.filter(user=self.user,
                                                   exam=self.exam).last().id
                }))

  def test_exam_page_get(self):
    """Check that method renders correctly."""

    response = self.client.get(
        reverse('exam_page', kwargs={'attempt_id': self.exam_attempt.id}))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('exam/exam_attempt.html')

  def test_exam_page_get_context(self):
    """Check that method returns correct context data."""

    response = self.client.get(
        reverse('exam_page', kwargs={'attempt_id': self.exam_attempt.id}))
    attempt = response.context['attempt']
    self.assertEqual(self.exam_attempt, attempt)
    self.assertEqual(self.exam_attempt.user, attempt.user)
    self.assertEqual(attempt.mode, ExamAttempt.PRACTICE_MODE)

  def test_exam_finish_get_unauthorized_user(self):
    """Check access denied for unauthorized user."""

    user = User.objects.get(id=5)
    self.client.login(username=user.username, password=self.password)
    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.exam_attempt.id}))
    self.assertEqual(response.status_code, 404)

  def test_exam_finish_get_not_all_questions(self):
    """Check that method returns 404 if exam is not finished."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.exam_attempt.id}))
    self.assertEqual(response.status_code, 404)
    self.assertTemplateUsed('exam/finish.html')

  def test_exam_attempt_finish_get(self):
    """Check that finish page for exam attempt renders correctly."""

    self.client.login(username=self.user.username, password=self.password)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.exam_attempt,
                                                  question=self.question)
    answer_attempt.answers.add(self.answer)
    answer_attempt.save()

    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.exam_attempt.id}))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('exam/finish.html')

  def test_exam_attempt_practice_mode_finish_get_context(self):
    """Check that method returns correct context."""

    self.client.login(username=self.user.username, password=self.password)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.exam_attempt,
                                                  question=self.question)
    answer_attempt.answers.add(self.answer)
    answer_attempt.save()

    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.exam_attempt.id}))

    self.assertEqual(response.context['grade'], self.exam_attempt.grade)
    self.assertEqual(
        response.context['status'],
        f"Congratulations! You've finished {ExamAttempt.PRACTICE_MODE} in {self.subject.name} {self.exam.name}! Your grade is {self.exam_attempt.grade}%."
    )

  def test_subject_attempt_exam_mode_finish_get_context(self):
    """Check that method returns correct context."""

    self.client.login(username=self.user.username, password=self.password)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.subject_attempt,
                                                  question=self.question)
    answer_attempt.answers.add(self.answer)
    answer_attempt.save()

    response = self.client.get(
        reverse('exam_finish', kwargs={'attempt_id': self.subject_attempt.id}))
    self.assertEqual(response.context['grade'], self.subject_attempt.grade)
    self.assertEqual(
        response.context['status'],
        f"Congratulations! You've finished {ExamAttempt.EXAM_MODE} in {self.subject.name} {self.exam.name}! Your grade is {self.subject_attempt.grade}%."
    )

  def test_get_attempt_unauthenticated(self):
    """Check access denied for unauthenticated user."""

    response = self.client.get(reverse('get_attempt', kwargs={'attempt_id': 1}))
    self.assertEqual(response.status_code, 403)

  def test_get_attempt_no_attempt(self):
    """Check case when there's no such attempt in DB."""

    self.client.login(username=self.user.username, password=self.password)
    response = self.client.get(reverse('get_attempt',
                                       kwargs={'attempt_id': 10}))
    self.assertEqual(response.status_code, 404)

  def test_get_attempt(self):
    """Check that method returns correct exam attempt."""

    self.client.login(username=self.user.username, password=self.password)
    answer_attempt = AnswerAttempt.objects.create(attempt=self.exam_attempt,
                                                  question=self.question)
    answer_attempt.answers.set([self.answer])

    response = self.client.get(
        reverse('get_attempt', kwargs={'attempt_id': self.exam_attempt.id}))

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data,
                     ExamAttemptSerializer(self.exam_attempt).data)
