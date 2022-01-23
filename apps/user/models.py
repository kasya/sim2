"""User model methods."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
  """User model."""

  requires_extra_time = models.BooleanField(default=False)

  def __str__(self):
    return f'{self.first_name} {self.last_name}, {self.id}'
