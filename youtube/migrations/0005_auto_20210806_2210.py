# Generated by Django 3.1.6 on 2021-08-07 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0004_rulecoltemplate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rulecollection',
            name='is_template',
        ),
        migrations.RemoveField(
            model_name='rulecollection',
            name='num_subscribers',
        ),
    ]
