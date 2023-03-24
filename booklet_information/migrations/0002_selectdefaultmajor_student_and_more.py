# Generated by Django 4.1.7 on 2023-03-22 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_reportcard_report_card_file'),
        ('booklet_information', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectdefaultmajor',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.student'),
        ),
        migrations.AddField(
            model_name='selectdefaultprovince',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.student'),
        ),
        migrations.AddField(
            model_name='selectprovinceformajor',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.student'),
        ),
    ]
