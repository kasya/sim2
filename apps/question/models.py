from django.db import models


class Answer(models.Model):
  """Answer model."""

  text = models.CharField(max_length=1000)

  def __str__(self):
    return f'<Answer>: {self.text}, id#{self.id}'


class Question(models.Model):
  """Question model."""

  MULTIPLE_CHOICE_TYPE = 'multiple_choice'
  MULTIPLE_SELECT_TYPE = 'multiple_select'

  QUESTION_TYPES = [
      (MULTIPLE_CHOICE_TYPE, 'Multiple choice'),
      (MULTIPLE_SELECT_TYPE, 'Multiple select'),
  ]

  text = models.CharField(max_length=1000)
  type = models.CharField(max_length=30,
                          default=MULTIPLE_CHOICE_TYPE,
                          choices=QUESTION_TYPES)
  weight = models.IntegerField(default=1)
  correct_answers = models.ManyToManyField(Answer,
                                           related_name='correct_answers')
  wrong_answers = models.ManyToManyField(Answer, related_name='wrong_answers')

  category = models.ForeignKey('QuestionCategory', on_delete=models.CASCADE)
  exam = models.ForeignKey('exam.Exam', on_delete=models.CASCADE)

  def __str__(self):
    return f'<Question>: {self.text}, id#{self.id}:'


class QuestionCategory(models.Model):
  """Question category model."""

  name = models.CharField(max_length=1000)

  def __str__(self):
    return f'<Category>: {self.name}, id#{self.id}'
