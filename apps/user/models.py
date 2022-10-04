"""User model methods."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
  """User model."""

  required_extra_time = models.IntegerField(verbose_name=_('required extra time'), default=0)

  class Meta:
    """Meta class for User model."""

    verbose_name = _('user')
    verbose_name_plural = _('users')

  def __str__(self):
    return _('{first_name} {self.last_name}, {self.id}').format(first_name=self.first_name, last_name=self.last_name, id=self.id)
