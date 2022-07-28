"""Tests for User app views."""

from django.test import Client, TestCase
from django.urls import reverse

from apps.exam.models import Exam, ExamAttempt
from apps.user.models import User


class UserViewTestCase(TestCase):
  """Test cases for user views."""

  client = Client()
  fixtures = [
      "answer.json", "answer_attempt.json", "exam.json", "exam_attempt.json",
      "question.json", "question_category.json", "subject.json", "user.json"
  ]

  user_id = 4
  user_password = 'mypassword'

  def test_login_get(self):
    """Check that login page renders correctly."""

    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/login.html')

  def test_login_post_correct_user(self):
    """Check that user logged in correctly and redirected to profile page."""

    user = User.objects.get(id=self.user_id)
    response = self.client.post(reverse('login'), {
        'email': user.email,
        'password': self.user_password,
    })
    self.assertRedirects(response, reverse('profile'))

  def test_login_post_invalid_password(self):
    """Check that invalid password redirects back to login."""

    user = User.objects.get(id=self.user_id)
    response = self.client.post(reverse('login'), {
        'email': user.email,
        'password': 'wrongpass',
    })
    self.assertTemplateUsed('user/login.html')
    self.assertEqual(response.status_code, 200)

  def test_logout_get(self):
    """Check that user logged out and redirected to login page."""

    user = User.objects.get(id=self.user_id)
    self.client.login(email=user.email, password=self.user_password)

    response = self.client.get(reverse('logout'))

    self.assertRedirects(response, reverse('login'))

  def test_profile_get_incognito(self):
    """Check that profile page is not available for unauthorized users."""

    response = self.client.get(reverse('profile'))
    self.assertRedirects(response,
                         f'{reverse("login")}?next={reverse("profile")}')

  def test_profile_get(self):
    """Check that profile page renders correctly."""

    user = User.objects.get(id=self.user_id)
    self.client.login(username=user.email, password=self.user_password)

    response = self.client.get(reverse('profile'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/profile.html')

  def test_profile_get_message(self):
    """Check that page shows greeting message with username."""

    user = User.objects.get(id=self.user_id)
    self.client.login(username=user.email, password=self.user_password)

    response = self.client.get(reverse('profile'))
    self.assertIn(f'Welcome, {user.first_name}',
                  response.content.decode('utf-8'))

  def test_signup_get(self):
    """Check that signup page renders correctly."""

    response = self.client.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/signup.html')

  def test_signup_post(self):
    """Check that user is redirected to login page after signing up
    and that user has been added to db."""

    response = self.client.post(
        reverse('signup'), {
            'email': 'test@email.com',
            'password': 'password',
            'first_name': 'Julie',
            'last_name': 'Doe',
        })
    self.assertRedirects(response, reverse('login'))
    self.assertEqual(User.objects.count(), 3)

  def test_signup_post_same_user(self):
    """Check that system doesn't add same user to db twice."""

    response = self.client.post(
        reverse('signup'), {
            'email': 'secondtest@email.com',
            'password': 'password',
            'first_name': 'Janice',
            'last_name': 'Doe',
        })
    self.assertRedirects(response, reverse('login'))

    response = self.client.post(
        reverse('signup'), {
            'email': 'secondtest@email.com',
            'password': 'password',
            'first_name': 'Janice',
            'last_name': 'Doe',
        })
    self.assertEqual(User.objects.count(), 3)
    self.assertIn('You already have an account with us.',
                  response.content.decode('utf-8'))
    self.assertTemplateUsed('user/signup.html')

  def test_profile_get_context(self):
    """Check that method updates context data. """

    user = User.objects.get(id=self.user_id)
    self.client.login(username=user.email, password=self.user_password)

    response = self.client.get(reverse('profile'))
    self.assertEqual(
        response.context['exams_count'],
        ExamAttempt.objects.filter(user=user).values('exam').distinct().count())
    self.assertEqual(
        response.context['exam_ids'],
        list(
            ExamAttempt.objects.filter(user=user).values_list('exam',
                                                              flat=True)))

  def test_profile_chart_get(self):
    """Check that method sends data to frontend."""

    user = User.objects.get(id=self.user_id)
    self.client.login(username=user.email, password=self.user_password)
    exam = Exam.objects.get(id=1)

    response = self.client.get(
        reverse('profile-chart', kwargs={'exam_id': exam.id}))

    self.assertEqual(response.data['exam_name'], exam.name)
    self.assertEqual(response.data['exam_subject'], exam.subject.name)

  def test_edit_profile_get_incognito(self):
    """Check that edit profile page is not available for unauthorized users."""

    response = self.client.get(reverse('edit-profile'))
    self.assertRedirects(response,
                         f'{reverse("login")}?next={reverse("edit-profile")}')

  def test_edit_profile_get(self):
    """Check that edit profile page renders correctly."""

    user = User.objects.get(id=self.user_id)
    self.client.login(username=user.email, password=self.user_password)

    response = self.client.get(reverse('edit-profile'))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/edit_profile.html')

  def test_edit_profile_post(self):
    """Check that user has been redirected to profile page after edit."""

    user = User.objects.get(id=self.user_id)
    print(user.first_name, user.last_name, user.username)
    self.client.login(username=user.email, password=self.user_password)

    response = self.client.post(reverse('edit-profile'), {
        'first_name': 'Janine',
        'last_name': 'Doe',
    })

    self.assertRedirects(response, reverse('profile'))

  def test_edit_profile_post_no_change(self):
    """Check that other profile details hasn't been changed after edit."""

    user = User.objects.get(id=self.user_id)
    test_user_username = user.username
    test_user_password = self.user_password

    self.client.login(email=user.email, password=self.user_password)

    response = self.client.post(reverse('edit-profile'), {
        'first_name': 'Jane',
        'last_name': 'Smith',
    })

    self.assertEquals(test_user_username, user.username)
    self.assertEquals(test_user_password, self.user_password)
