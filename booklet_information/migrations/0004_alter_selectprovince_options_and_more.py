# Generated by Django 4.1.1 on 2023-05-13 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booklet_information', '0003_majorselection'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='selectprovince',
            options={'ordering': ('index',)},
        ),
        migrations.AlterField(
            model_name='selectprovinceformajor',
            name='select_province',
            field=models.ManyToManyField(blank=True, null=True, to='booklet_information.selectprovince'),
        ),
    ]
