"""User model methods."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
  """User model."""

  required_extra_time = models.IntegerField(default=0)

  def __str__(self):
    return f'{self.first_name} {self.last_name}, {self.id}'
