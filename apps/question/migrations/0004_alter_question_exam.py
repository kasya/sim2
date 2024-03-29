# Generated by Django 4.0.1 on 2022-02-09 23:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exam", "0003_exam_question_count_and_more"),
        ("question", "0003_alter_question_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="exam",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="exam.exam",
            ),
        ),
    ]
