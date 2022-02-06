"""Tests for User app models."""

from apps.user.models import User
from django.test import TestCase


class UserModelTestCase(TestCase):
  """Test cases for user models."""

  fixtures = ["user.json"]

  def test_user_model(self):
    """Unit test for User model."""

    user = User.objects.get(id=4)

    self.assertEqual(str(user), 'jack doe, 4')
