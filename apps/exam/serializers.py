from rest_framework import serializers

from apps.exam.models import Exam, Subject


class ExamSerializer(serializers.ModelSerializer):

  class Meta:
    model = Exam
    fields = ('id', 'name')


class SubjectSerializer(serializers.ModelSerializer):

  class Meta:
    model = Subject
    fields = ('id', 'name')
