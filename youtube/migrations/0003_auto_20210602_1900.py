# Generated by Django 3.1.6 on 2021-06-03 02:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0002_comment_likecount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='id',
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_id',
            field=models.CharField(default=1, max_length=100, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('text', models.CharField(max_length=5000)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('author', models.CharField(max_length=200)),
                ('likeCount', models.IntegerField()),
                ('reply_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube.comment')),
            ],
        ),
    ]