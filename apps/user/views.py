"""User views methods."""

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exam.models import Exam, ExamAttempt
from apps.user.forms import LoginForm, SignupForm


class Login(LoginView):
  """Login methods."""

  form_class = LoginForm
  template_name = 'user/login.html'

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


class Profile(LoginRequiredMixin, ListView):
  """Profile methods."""

  paginate_by = 10
  template_name = 'user/profile.html'

  def get_context_data(self, **kwargs):
    """Render profile page."""

    exam_ids = ExamAttempt.objects.filter(
        user=self.request.user).values('exam').distinct()[:2]
    context = super().get_context_data(**kwargs)
    context.update({
        'exams_count':
            len(
                ExamAttempt.objects.filter(
                    user=self.request.user).values('exam').distinct()),
        'exam_ids': [exam['exam'] for exam in exam_ids],
        'name':
            self.request.user.first_name,
    })

    return context

  def get_queryset(self):
    return ExamAttempt.objects.filter(
        user=self.request.user).order_by('-created')


class ProfileChart(APIView):

  permission_classes = (IsAuthenticated,)

  def get(self, request, exam_id):
    """Sends attempts data to frontend for charts."""
    attempts = ExamAttempt.objects.filter(exam=exam_id,
                                          user_id=request.user.id)[:50]
    data = {
        'dates': (attempt.created.strftime("%b %d %Y") for attempt in attempts),
        'grades': (attempt.grade for attempt in attempts),
        'exam_name': Exam.objects.get(id=exam_id).name
    }
    return Response(data)


class Signup(TemplateView):
  """Signup methods."""

  form_class = SignupForm
  template_name = 'user/signup.html'

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


class ProgressCharts(ListView):

  template_name = 'user/progress_charts.html'
  paginate_by = 2

  def get_queryset(self):
    """Return list of exam ids for current user."""

    return list(
        ExamAttempt.objects.filter(user=self.request.user).values_list(
            'exam', flat=True).distinct())
