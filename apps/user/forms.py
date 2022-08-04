"""Forms for user app."""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.forms import ModelForm
from django.urls import reverse

from apps.user.models import User


class LoginForm(ModelForm):
  """User login form."""

  remember = forms.BooleanField(label='Remember me', required=False)

  def clean(self):
    cleaned_data = super().clean()
    if not authenticate(username=self.cleaned_data['email'],
                        password=self.cleaned_data['password']):
      raise forms.ValidationError('Invalid login or password.')

    return cleaned_data

  def login(self, request):
    """User login method."""

    user = authenticate(username=self.cleaned_data['email'],
                        password=self.cleaned_data['password'])
    auth_login(request, user)

    if self.cleaned_data['remember']:
      request.session.set_expiry(86400 * 7)

    return reverse('profile')

  class Meta:
    """Meta class for Login form."""

    model = User
    fields = ['email', 'password']
    widgets = {
        'password': forms.PasswordInput(),
    }


class SignupForm(ModelForm):
  """User signup form."""

  def clean_email(self):
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).exists():
      raise forms.ValidationError('You already have an account with us.')

    return email

  def save(self, commit=True):
    user = super().save(commit=False)

    user.set_password(self.cleaned_data['password'])
    user.username = self.cleaned_data['email']

    if commit:
      user.save()

    return user

  class Meta:
    """Meta class for Signup form."""

    model = User
    fields = ('email', 'password', 'first_name', 'last_name')
    widgets = {
        'password': forms.PasswordInput(),
    }


class EditProfileForm(ModelForm):
  """User Edit Profile form."""

  class Meta:
    """Meta class for Edit Profile form."""
    model = User
    fields = (
        'first_name',
        'last_name',
    )
