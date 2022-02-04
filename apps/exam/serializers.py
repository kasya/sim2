from rest_framework import serializers

from apps.exam.models import Exam, ExamAttempt, Subject


class ExamSerializer(serializers.ModelSerializer):

  class Meta:
    model = Exam
    fields = ('id', 'name')


class SubjectSerializer(serializers.ModelSerializer):

  class Meta:
    model = Subject
    fields = ('id', 'name')


class ExamAttemptSerializer(serializers.ModelSerializer):

  questions = serializers.Serializer()
  time_left_seconds = serializers.SerializerMethodField()
  attempt_duration_minutes = serializers.SerializerMethodField()
  question_count = serializers.SerializerMethodField()

  def get_question_count(self, obj):
    return obj.questions.count()

  def get_time_left_seconds(self, obj):
    return obj.time_left_seconds

  def get_attempt_duration_minutes(self, obj):
    return obj.duration_minutes

  class Meta:
    model = ExamAttempt
    fields = ('user', 'exam', 'questions', 'time_left_seconds',
              'attempt_duration_minutes', 'question_count')
