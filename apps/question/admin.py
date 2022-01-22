from django.contrib import admin

from apps.question.models import Answer, Question, QuestionCategory

admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(QuestionCategory)
