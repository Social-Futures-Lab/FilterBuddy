# Generated by Django 3.1.6 on 2021-06-07 22:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0005_rulecollection_is_template'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rulecollection',
            name='is_template',
        ),
    ]
