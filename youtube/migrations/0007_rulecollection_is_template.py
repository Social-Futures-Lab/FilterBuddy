# Generated by Django 3.1.6 on 2021-06-07 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0006_remove_rulecollection_is_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulecollection',
            name='is_template',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
