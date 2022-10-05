from django.db import models
from django.utils.translation import gettext_lazy as _


class Answer(models.Model):
  """Answer model."""

  text = models.CharField(verbose_name=_('text'), max_length=1000)
  class Meta:
    """Meta class for Answer model."""

    verbose_name = _('answer')
    verbose_name_plural = _('answers')

  def __str__(self):
    return _('<Answer>: {text}, id# {id}').format(text=self.text, id=self.id)


class Question(models.Model):
  """Question model."""

  MULTIPLE_CHOICE_TYPE = 'multiple_choice'
  MULTIPLE_SELECT_TYPE = 'multiple_select'

  QUESTION_TYPES = [
      (MULTIPLE_CHOICE_TYPE, _('Multiple choice')),
      (MULTIPLE_SELECT_TYPE, _('Multiple select')),
  ]

  text = models.CharField(verbose_name=_('text'), max_length=1000)
  type = models.CharField(verbose_name=_('type'), max_length=30,
                          default=MULTIPLE_CHOICE_TYPE,
                          choices=QUESTION_TYPES)
  weight = models.IntegerField(verbose_name=_('weight'), default=1)
  correct_answers = models.ManyToManyField(Answer,
                                           related_name='correct_answers')
  wrong_answers = models.ManyToManyField(Answer, related_name='wrong_answers')

  category = models.ForeignKey('QuestionCategory', on_delete=models.CASCADE)
  exam = models.ForeignKey('exam.Exam',
                           related_name='questions',
                           on_delete=models.CASCADE)
  class Meta:
    """Meta class for Question model."""

    verbose_name = _('question')
    verbose_name_plural = _('questions')

  def __str__(self):
    return _('<Question>: {text}, id# {id}:').format(text=self.text, id=self.id)

  def correct_answer_ids(self):
    return (answer.id for answer in self.correct_answers.all())


class QuestionCategory(models.Model):
  """Question category model."""

  name = models.CharField(verbose_name=_('name'), max_length=1000)
  class Meta:
    """Meta class for Question Category model."""

    verbose_name = _('question category')
    verbose_name_plural = _('question categories')

  def __str__(self):
    return _('<Category>: {name}, id# {id}').format(name=self.name, id=self.id)
