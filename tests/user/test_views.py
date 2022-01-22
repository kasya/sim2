"""Tests for User app views."""

from apps.user.models import User
from django.contrib.auth import login
from django.test import Client, TestCase
from django.urls import reverse


class UserViewTestCase(TestCase):
  """Test cases for user views."""

  client = Client()

  def test_login_get(self):
    """Check that login page renders correctly."""

    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/login.html')

  def test_login_post(self):
    """Check that user logged in correctly and redirected to profile page."""

    username = 'john@test.com'
    password = 'smith'

    user = User.objects.create_user(username=username, password=password)
    response = self.client.post(reverse('login'), {
        'email': username,
        'password': password,
    })

    self.assertRedirects(response, reverse('profile'))

  def test_logout_get(self):
    """Check that user logged out and redirected to login page."""

    username = 'john@test.com'
    password = 'smith'

    user = User.objects.create_user(username=username, password=password)
    self.client.login(email=username, password=password)

    response = self.client.get(reverse('logout'))

    self.assertRedirects(response, reverse('login'))

  def test_profile_get(self):
    """Check that profile page renders correctly."""

    response = self.client.get(reverse('profile'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/profile.html')

  def test_signup_get(self):
    """Check that signup page renders correctly."""

    response = self.client.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/signup.html')

  def test_signup_post(self):
    """Check that user is signed up and added to database."""

    # Signup user.
    username = 'john@test.com'
    password = 'smith'
    firstname = 'john'
    lastname = 'smith'

    response = self.client.post(
        reverse('signup'), {
            'email': username,
            'password': password,
            'first_name': firstname,
            'last_name': lastname,
        })
    self.assertRedirects(response, reverse('login'))
    self.assertEqual(User.objects.count(), 1)

    # try to signup same user again.
    response = self.client.post(
        reverse('signup'), {
            'email': username,
            'password': password,
            'first_name': firstname,
            'last_name': lastname,
        })
    self.assertEqual(User.objects.count(), 1)
