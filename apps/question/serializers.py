import random

from rest_framework import serializers

from apps.question.models import Answer, Question


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model."""

    class Meta:
        model = Answer
        fields = ("id", "text")


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""

    answers = serializers.SerializerMethodField()

    def get_answers(self, obj):
        """Combine correct and wrong answers and shuffle them."""

        answers = list(obj.correct_answers.all())
        answers.extend(obj.wrong_answers.all())
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data

    class Meta:
        model = Question
        fields = ("id", "text", "type", "answers")
