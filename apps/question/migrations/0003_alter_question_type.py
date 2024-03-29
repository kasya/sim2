# Generated by Django 4.0.1 on 2022-01-24 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0002_question_exam"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="type",
            field=models.CharField(
                choices=[
                    ("multiple_choice", "Multiple choice"),
                    ("multiple_select", "Multiple select"),
                ],
                default="multiple_choice",
                max_length=30,
            ),
        ),
    ]
