from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exam.models import AnswerAttempt, ExamAttempt
from apps.question.models import Answer
from apps.question.serializers import QuestionSerializer


class QuestionView(APIView):
  """Question object view."""

  permission_classes = (IsAuthenticated,)

  def dispatch(self, request, *args, **kwargs):

    self.attempt = get_object_or_404(ExamAttempt,
                                     id=self.kwargs['attempt_id'],
                                     user=request.user.id)
    return super().dispatch(request, *args, **kwargs)

  def get(self, request, **kwargs):
    """Send a question object to frontend."""

    answered_questions = [
        aa.question.id
        for aa in AnswerAttempt.objects.filter(attempt=self.attempt)
    ]

    for question in self.attempt.questions.all():
      if question.id in answered_questions:
        continue
      return Response(QuestionSerializer(question).data)

    return Response(status=status.HTTP_200_OK)

  def post(self, request, **kwargs):
    """Save answers to AnswerAttempt."""

    data = request.data
    answer_ids = data.get('answers')

    if not data or not answer_ids:
      raise Http404

    if not self.attempt.time_left_seconds:
      raise Http404

    answer_attempts = AnswerAttempt.objects.filter(attempt=self.attempt,
                                                   question=data['question_id'])

    if set(answer_attempts) == set(answer_ids):
      return Response(status=status.HTTP_200_OK)

    for answer in answer_attempts:
      answer.delete()

    aa = AnswerAttempt.objects.create(attempt_id=self.attempt.id,
                                      question_id=data['question_id'])
    for answer_id in answer_ids:
      aa.answers.add(Answer.objects.get(id=answer_id))

    return Response(status=status.HTTP_201_CREATED)
