# Generated by Django 3.0.1 on 2020-07-31 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20200731_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='description',
            field=models.CharField(default='', max_length=500),
        ),
    ]
