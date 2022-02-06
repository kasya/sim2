"""Tests for User app views."""

from django.test import Client, TestCase
from django.urls import reverse

from apps.user.models import User


class UserViewTestCase(TestCase):
  """Test cases for user views."""

  client = Client()
  fixtures = ["user.json"]

  def test_login_get(self):
    """Check that login page renders correctly."""

    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/login.html')

  def test_login_post_correct_user(self):
    """Check that user logged in correctly and redirected to profile page."""

    user = User.objects.get(id=4)
    response = self.client.post(reverse('login'), {
        'email': user.email,
        'password': 'mypassword',
    })
    self.assertRedirects(response, reverse('profile'))

  def test_login_post_invalid_password(self):
    """Check that invalid password redirects back to login."""

    user = User.objects.get(id=4)
    response = self.client.post(reverse('login'), {
        'email': user.email,
        'password': 'wrongpass',
    })
    self.assertTemplateUsed('user/login.html')
    self.assertEqual(response.status_code, 200)

  def test_logout_get(self):
    """Check that user logged out and redirected to login page."""

    user = User.objects.get(id=4)
    self.client.login(email=user.email, password='mypassword')

    response = self.client.get(reverse('logout'))

    self.assertRedirects(response, reverse('login'))

  def test_profile_get_incognito(self):
    """Check that profile page is not available for unauthorized users."""

    response = self.client.get(reverse('profile'))
    self.assertRedirects(response,
                         f'{reverse("login")}?next={reverse("profile")}')

  def test_profile_get(self):
    """Check that profile page renders correctly."""

    user = User.objects.get(id=4)
    self.client.login(username=user.email, password='mypassword')

    response = self.client.get(reverse('profile'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/profile.html')

  def test_profile_get_message(self):
    """Check that page shows greeting message with username."""

    user = User.objects.get(id=4)
    self.client.login(username=user.email, password='mypassword')

    response = self.client.get(reverse('profile'))
    self.assertIn(f'Hello, {user.email}', response.content.decode('utf-8'))

  def test_signup_get(self):
    """Check that signup page renders correctly."""

    response = self.client.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('user/signup.html')

  def test_signup_post(self):
    """Check that user is redirected to login page after signing up
    and that user has been added to db.."""

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
            'email': 'test@email.com',
            'password': 'password',
            'first_name': 'Julie',
            'last_name': 'Doe',
        })
    self.assertEqual(User.objects.count(), 3)
    self.assertTemplateUsed('user/signup.html')
