# Generated by Django 3.1.6 on 2021-08-04 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0002_auto_20210804_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulecollection',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
