# Generated by Django 4.1.1 on 2023-08-24 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_student_field_of_study_alter_user_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='field_of_study',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'ریاضی'), (1, 'تجربی'), (2, 'انسانی'), (3, 'هنر'), (4, 'زبان'), (5, 'ریاضی 1'), (6, 'ریاضی و فیزیک'), (7, 'ریاضی جدید')], null=True),
        ),
    ]