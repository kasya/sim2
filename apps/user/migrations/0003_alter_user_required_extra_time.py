# Generated by Django 4.0.1 on 2022-10-03 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_remove_user_requires_extra_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="required_extra_time",
            field=models.IntegerField(
                default=0, verbose_name="required extra time"
            ),
        ),
    ]
