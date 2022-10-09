# Generated by Django 4.0.1 on 2022-01-21 19:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="QuestionCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=1000)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("multiple_choice", "multiple_choice"),
                            ("multiple_select", "multiple_select"),
                        ],
                        default="multiple_choice",
                        max_length=30,
                    ),
                ),
                ("weight", models.IntegerField(default=1)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="question.questioncategory",
                    ),
                ),
                (
                    "correct_answers",
                    models.ManyToManyField(
                        related_name="correct_answers", to="question.Answer"
                    ),
                ),
                (
                    "wrong_answers",
                    models.ManyToManyField(
                        related_name="wrong_answers", to="question.Answer"
                    ),
                ),
            ],
        ),
    ]
