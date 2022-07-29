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

  def get(self, request, **kwargs):
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
    """Get context."""

    show_charts = 2
    exam_ids = ExamAttempt.objects.filter(user=self.request.user).values_list(
        'exam', flat=True).distinct()[:show_charts]
    context = super().get_context_data(**kwargs)
    context.update({
        'exams_count':
            ExamAttempt.objects.filter(user=self.request.user
                                      ).values('exam').distinct().count(),
        'exam_ids':
            list(exam_ids)
    })

    return context

  def get_queryset(self):
    return ExamAttempt.objects.filter(
        user=self.request.user).order_by('-created')


class ProfileChart(APIView):

  permission_classes = (IsAuthenticated,)

  def get(self, request, exam_id):
    """Sends attempts data to frontend for charts."""
    show_entries = 50
    attempts = ExamAttempt.objects.filter(
        exam=exam_id, user_id=request.user.id)[:show_entries]
    exam = Exam.objects.get(id=exam_id)
    data = {
        'dates': (attempt.created.strftime('%b %d %Y') for attempt in attempts),
        'grades': (attempt.grade for attempt in attempts),
        'exam_name': exam.name,
        'exam_subject': exam.subject.name
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

  paginate_by = 2
  template_name = 'user/progress_charts.html'

  def get_queryset(self):
    """Return list of exam ids for current user."""

    return list(
        ExamAttempt.objects.filter(user=self.request.user).select_related(
            'exam', 'exam__subject').values_list('exam', flat=True).distinct())
