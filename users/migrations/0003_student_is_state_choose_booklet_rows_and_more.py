# Generated by Django 4.1.7 on 2023-03-24 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_reportcard_report_card_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_state_choose_booklet_rows',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='is_state_choose_booklet_rows_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='is_state_choose_default',
            field=models.BooleanField(default=False),
        ),
    ]
