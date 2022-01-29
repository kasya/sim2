from django.http import Http404
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

  def get(self, request, attempt_id):
    """Send a question object to frontend."""

    attempt = ExamAttempt.objects.get(id=attempt_id)
    if request.user.id != attempt.user.id:
      raise Http404

    attempted_answers = AnswerAttempt.objects.filter(attempt=attempt_id)
    answered_questions = [aa.question.id for aa in attempted_answers]

    for question in attempt.questions.all():
      if question.id in answered_questions:
        continue
      return Response(QuestionSerializer(question).data)

  def post(self, request, attempt_id):
    """Save answers to AnswerAttempt."""

    data = request.data
    answer_ids = data.get('answers')

    if not data or not answer_ids:
      raise Http404

    attempt = ExamAttempt.objects.get(id=attempt_id)

    if not attempt.time_left_seconds:
      raise Http404

    question_id = data.get('question_id')
    answer_attempts = AnswerAttempt.objects.filter(question=question_id,
                                                   attempt=attempt_id)

    if set(answer_attempts) == set(answer_ids):
      return Response(status=status.HTTP_201_CREATED)

    for answer in answer_attempts:
      answer.delete()

    aa = AnswerAttempt.objects.create(attempt_id=attempt_id,
                                      question_id=question_id)
    for answer_id in answer_ids:
      aa.answers.add(Answer.objects.get(id=answer_id))

    return Response(status=status.HTTP_201_CREATED)
