# Generated by Django 3.1.6 on 2021-08-07 03:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0003_auto_20210804_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuleColTemplate',
            fields=[
                ('rulecollection_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='youtube.rulecollection')),
                ('num_users', models.IntegerField()),
            ],
            bases=('youtube.rulecollection',),
        ),
    ]
