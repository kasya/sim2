from django import forms
from django.forms import ModelForm

from .models import User


class LoginForm(ModelForm):

  class Meta:
    model = User
    fields = ['email', 'password']
    widgets = {
        'password': forms.PasswordInput(),
    }


form = LoginForm()
