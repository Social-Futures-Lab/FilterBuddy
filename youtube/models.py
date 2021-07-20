from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Channel(models.Model):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=5000)
    pub_date = models.DateTimeField('date published')
    channel_id = models.CharField(max_length=100, primary_key=True)
#    user = models.ForeignKey(User)

    def __str__(self):
        return u'%s' % (self.title)
        
class RuleCollection(models.Model):
    title = models.CharField(max_length=500)
    pub_date = models.DateTimeField('date published')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=True, null=True)
    is_template = models.BooleanField()

    def __str__(self):
        return u'%s' % (self.title)

class Rule(models.Model):
    phrase = models.CharField(max_length=500)
    exception_phrase = models.CharField(max_length=500, blank=True, null=True)
    rule_collection = models.ForeignKey(RuleCollection, on_delete=models.CASCADE)
    
    def __str__(self):
        return u'%s %s' % (self.phrase, self.rule_collection)

class Video(models.Model):
    title = models.CharField(max_length=500)
    pub_date = models.DateTimeField('date published')
    video_id = models.CharField(max_length=100, primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

class Comment(models.Model):
    text = models.CharField(max_length=5000)
    pub_date = models.DateTimeField('date published')
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    likeCount = models.IntegerField()
    comment_id = models.CharField(max_length=100, primary_key=True)
    thread_id = models.CharField(max_length=100)

class Reply(models.Model):
    text = models.CharField(max_length=5000)
    pub_date = models.DateTimeField('date published')
    author = models.CharField(max_length=200)
    likeCount = models.IntegerField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reply_id = models.CharField(max_length=100, primary_key=True)
