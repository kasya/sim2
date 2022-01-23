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

    email = 'john@test.com'
    password = 'smith'

    User.objects.create_user(username=email, password=password)
    response = self.client.post(reverse('login'), {
        'email': email,
        'password': password,
    })
    self.assertRedirects(response, reverse('profile'))

    response = self.client.get(reverse('profile'))
    self.assertInHTML('Logout', response.content.decode('utf-8'))

  def test_logout_get(self):
    """Check that user logged out and redirected to login page."""

    email = 'john@test.com'
    password = 'smith'

    User.objects.create_user(username=email, password=password)
    self.client.login(email=email, password=password)

    response = self.client.get(reverse('logout'))

    self.assertRedirects(response, reverse('login'))

  def test_profile_get(self):
    """Check that profile page renders correctly."""

    # try to access page incognito.
    response = self.client.get(reverse('profile'))
    self.assertRedirects(response, '/login?next=/profile')

    # login user and try to access page.
    email = 'john@test.com'
    password = 'smith'

    user = User.objects.create_user(username=email, password=password)
    self.client.login(username=email, password=password)

    response = self.client.get(reverse('profile'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/profile.html')
    self.assertIn(f'Hello, {email}', response.content.decode('utf-8'))

  def test_signup_get(self):
    """Check that signup page renders correctly."""

    response = self.client.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/signup.html')

  def test_signup_post(self):
    """Check that user is signed up and added to database."""

    # Signup user.
    email = 'john@test.com'
    password = 'smith'
    first_name = 'john'
    last_name = 'smith'

    response = self.client.post(
        reverse('signup'), {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
        })
    self.assertRedirects(response, reverse('login'))
    self.assertEqual(User.objects.count(), 1)

    # try to signup same user again.
    response = self.client.post(
        reverse('signup'), {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
        })
    self.assertEqual(User.objects.count(), 1)
