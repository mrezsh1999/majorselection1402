# Generated by Django 4.1.7 on 2023-05-13 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_student_is_state_choose_booklet_rows_and_more'),
        ('booklet_information', '0005_alter_selectprovince_province_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selectprovince',
            name='province',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='booklet_information.province'),
        ),
        migrations.AlterField(
            model_name='selectprovinceformajor',
            name='major',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='booklet_information.major'),
        ),
        migrations.AlterField(
            model_name='selectprovinceformajor',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.student'),
        ),
    ]
