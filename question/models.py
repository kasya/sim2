from django.db import models


class Answer(models.Model):
  """Answer model."""

  is_correct = models.BooleanField(default=False)
  question = models.ForeignKey('Question', on_delete=models.CASCADE)
  text = models.CharField(max_length=1000)

  def __repr__(self):
    return '"({}) {}".format("C" if self.is_correct else "I", self.text[:100])'


class Question(models.Model):
  """Question model."""

  MULTIPLE_CHOICE_TYPE = 'multiple_choice'
  MULTIPLE_SELECT_TYPE = 'multiple_select'

  text = models.CharField(max_length=1000)
  weight = models.IntegerField(default=1)
  type = models.CharField(max_length=30, default=MULTIPLE_CHOICE_TYPE)

  category = models.ForeignKey('QuestionCategory', on_delete=models.CASCADE)

  def __repr__(self):
    return f'Question #{self.id}: {self.text}'


class QuestionCategory(models.Model):
  """Question category model."""

  name = models.CharField(max_length=1000)

  def __repr__(self):
    return f'<Category>: {self.name}'
