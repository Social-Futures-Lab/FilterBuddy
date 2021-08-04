from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Channel(models.Model):
  title = models.CharField(max_length=500)
  description = models.CharField(max_length=5000)
  pub_date = models.DateTimeField('date published')
  channel_id = models.CharField(max_length=100, primary_key=True)

  def __str__(self):
    return u'%s' % (self.title)

class RuleCollection(models.Model):
  name = models.CharField(max_length=500)
  create_date = models.DateTimeField('date published')
  owner = models.ForeignKey(Channel, on_delete=models.CASCADE, blank=True, null=True)
  is_template = models.BooleanField()
  description = models.TextField(default="", blank=True, null=True)
  num_subscribers = models.IntegerField(default=0)

  def __str__(self):
    return u'%s' % (self.name)

class Rule(models.Model):
  phrase = models.CharField(max_length=500)
  exception_phrase = models.CharField(max_length=500, blank=True, null=True)
  rule_collection = models.ForeignKey(RuleCollection, on_delete=models.CASCADE)
  case_sensitive = models.BooleanField(default=False)
  spell_variants = models.BooleanField(default=True)

  def __str__(self):
    return u'%s %s' % (self.phrase, self.rule_collection)

class Video(models.Model):
  title = models.CharField(max_length=500)
  pub_date = models.DateTimeField('date published')
  video_id = models.CharField(max_length=100)
  channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

  def url_id_and_title(self):
    return 'stuff'

class Comment(models.Model):
  text = models.CharField(max_length=5000)
  pub_date = models.DateTimeField('date published')
  author = models.CharField(max_length=200)
  likeCount = models.IntegerField()
  comment_id = models.CharField(max_length=100)
  video = models.ForeignKey(Video, on_delete=models.CASCADE)
  parent_id = models.CharField(max_length=100, blank=True)

  def matched_phrases(self):
    return []  