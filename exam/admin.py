from django.contrib import admin

from exam.models import AnswerAttempt, Exam, ExamAttempt, Subject

admin.site.register(AnswerAttempt)
admin.site.register(Exam)
admin.site.register(ExamAttempt)
admin.site.register(Subject)
