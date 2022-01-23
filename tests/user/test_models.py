"""Tests for User app models."""

from apps.user.models import User
from django.test import TestCase


class UserModelTestCase(TestCase):
  """Test cases for user models."""

  def test_user_model(self):
    """Unit test for User model."""

    username = 'john@test.com'
    password = 'smith'
    firstname = 'john'
    lastname = 'smith'
    user = User.objects.create_user(username=username,
                                    password=password,
                                    first_name=firstname,
                                    last_name=lastname)

    self.assertEqual(str(user), f"{firstname} {lastname}, 1")
