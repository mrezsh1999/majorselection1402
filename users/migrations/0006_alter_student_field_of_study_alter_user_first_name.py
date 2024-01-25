# Generated by Django 4.1.1 on 2023-08-23 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_otp_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='field_of_study',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'ریاضی'), (1, 'تجربی'), (2, 'انسانی'), (3, 'هنر'), (4, 'زبان'), (5, 'ریاضی 1'), (6, 'ریاضی و فیزیک')], null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='first name'),
        ),
    ]
