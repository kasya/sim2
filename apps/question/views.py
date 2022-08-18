"""Question Views Methods."""

from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exam.models import AnswerAttempt, ExamAttempt
from apps.question.models import Answer, Question
from apps.question.serializers import QuestionSerializer


class APIAttemptBase(APIView):
  """Base API View class."""

  permission_classes = (IsAuthenticated,)

  def dispatch(self, request, *args, **kwargs):

    self.attempt = get_object_or_404(ExamAttempt,
                                     id=self.kwargs['attempt_id'],
                                     user=request.user.id)
    return super().dispatch(request, *args, **kwargs)


class QuestionView(APIAttemptBase):
  """Question object view."""

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
    if self.attempt.in_exam_mode and not self.attempt.time_left_seconds:
      raise Http404

    if not data or not answer_ids:
      raise Http404

    # Try to update an existing answer attempt.
    try:
      answer_attempt = AnswerAttempt.objects.prefetch_related('answers').get(
          attempt=self.attempt, question=data['question_id'])

      if set((a.id for a in answer_attempt.answers.all())) == set(answer_ids):
        return Response(status=status.HTTP_200_OK)

      answer_attempt.answers.set(Answer.objects.filter(id__in=answer_ids))
      return Response(status=status.HTTP_200_OK)
    except AnswerAttempt.DoesNotExist:
      pass

    # Create a new answer attempt.
    answer_attempt = AnswerAttempt.objects.create(
        attempt_id=self.attempt.id, question_id=data['question_id'])
    for answer_id in answer_ids:
      answer_attempt.answers.add(Answer.objects.get(id=answer_id))

    return Response(status=status.HTTP_201_CREATED)


class QuestionAnswerView(APIAttemptBase):
  """Question and Answer objects view."""

  def get(self, request, **kwargs):
    """Returns answered question and picked answers from AttemptAnswer."""

    question = get_object_or_404(Question, id=self.kwargs['question_id'])

    if question not in self.attempt.questions.all():
      raise Http404

    answer_attempt = AnswerAttempt.objects.get(attempt=self.attempt.id,
                                               question=question.id)

    answer_ids = [answer.id for answer in answer_attempt.answers.all()]
    return Response({
        'answer_ids': answer_ids,
        'question': QuestionSerializer(question).data
    })


class CheckAnswerView(APIView):

  def post(self, request, **kwargs):

    data = request.data
    question = Question.objects.get(id=self.kwargs['question_id'])
    correct_answer_ids = (int(answer_id) for answer_id in data['answer_ids'])
    if set(correct_answer_ids) == set((question.correct_answer_ids())):
      return Response({'result': 'correct'})

    return Response({
        'result':
            'wrong',
        'correct_answers': [
            answer.text for answer in question.correct_answers.all()
        ]
    })
