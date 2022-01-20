"""User views methods."""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from user.forms import LoginForm


class Login(TemplateView):
  """Login methods."""

  form_class = LoginForm
  initial = {'key': 'value'}
  template_name = "login.html"

  def get(self, request):
    """Render login page."""

    form = self.form_class(initial=self.initial)
    return render(request, self.template_name, {'form': form})

  def post(self, request):
    """Get the data from login form and check if we have this user in db.
    Then login user and redirect to Profile page."""

    form = self.form_class(request.POST)
    if form.is_valid():
      return redirect('profile')

    return render(request, self.template_name, {'form': form})
