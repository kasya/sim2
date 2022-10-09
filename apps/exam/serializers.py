"""Serializers for Exam module objects."""
from rest_framework import serializers

from apps.exam.models import AnswerAttempt, Exam, ExamAttempt, Subject


class AnswerAttemptSerializer(serializers.ModelSerializer):
    """AnswerAttempt Serializer."""

    class Meta:
        model = AnswerAttempt
        fields = ("question",)


class ExamSerializer(serializers.ModelSerializer):
    """Exam Serializer."""

    class Meta:
        model = Exam
        fields = ("id", "name")


class SubjectSerializer(serializers.ModelSerializer):
    """Subject Serializer."""

    class Meta:
        model = Subject
        fields = ("id", "name")


class ExamAttemptSerializer(serializers.ModelSerializer):
    """ExamAttempt Serializer."""

    answer_attempts = serializers.SerializerMethodField()
    attempt_duration_minutes = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    time_left_seconds = serializers.SerializerMethodField()

    def get_question_count(self, obj):
        """Return number of questions in current exam attempt."""

        return obj.questions.count()

    def get_time_left_seconds(self, obj):
        """Return time left in seconds for current exam attempt."""

        return obj.time_left_seconds

    def get_attempt_duration_minutes(self, obj):
        """Return attempt duration in minutes for current exam attempt."""

        return obj.duration_minutes

    def get_answer_attempts(self, obj):
        """Return AnswerAttempts in current exam attempt."""

        return [
            AnswerAttemptSerializer(obj).data
            for obj in obj.answerattempt_set.all()
        ]

    def get_mode(self, obj):
        return obj.mode

    class Meta:
        model = ExamAttempt
        fields = (
            "answer_attempts",
            "attempt_duration_minutes",
            "exams",
            "flagged_questions",
            "mode",
            "time_left_seconds",
            "questions",
            "question_count",
            "user",
        )
