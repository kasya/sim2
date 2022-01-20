"""User views methods."""
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import CreateView, TemplateView

from user.forms import LoginForm, SignupForm


class Login(TemplateView):
  """Login methods."""

  form_class = LoginForm
  template_name = 'login.html'

  def get(self, request):
    """Render login page."""

    form = self.form_class()
    return render(request, self.template_name, {'form': form})

  def post(self, request):
    """Get the data from login form and check if we have this user in db.
    Then login user and redirect to Profile page."""

    form = self.form_class(request.POST)
    if form.is_valid():
      return redirect(form.login(request))

    return render(request, self.template_name, {'form': form})


class Logout(TemplateView):
  """Logout methods."""

  def get(self, request):
    logout(request)
    return redirect('login')


class Profile(TemplateView):
  """Profile methods."""

  template_name = 'profile.html'

  def get(self, request):
    """Render profile page."""

    return render(request, self.template_name)


class Signup(TemplateView):
  """Signup methods."""

  form_class = SignupForm
  template_name = 'signup.html'

  def get(self, request):
    """Render signup page."""

    form = self.form_class()
    return render(request, self.template_name, {'form': form})

  def post(self, request):
    """Get the data from Signup form and add it to database."""

    form = self.form_class(request.POST)

    if form.is_valid():
      form.save()
      return redirect('login')

    return render(request, self.template_name, {'form': form})
