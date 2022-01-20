from django import forms
from django.forms import ModelForm

from user.models import User


class LoginForm(ModelForm):

  class Meta:
    model = User
    fields = ['email', 'password']
    widgets = {
        'password': forms.PasswordInput(),
    }
