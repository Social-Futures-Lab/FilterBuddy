from django.db import models
from django.contrib.auth.models import User
import re

# Create your models here.

def variantReg(phrase):
  myList = []
  for k in phrase:
    myList.append(k)
    myList.append('+')
  myString = ""
  for elem in myList:
    myString += elem
  return myString  

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
  description = models.TextField(default="", blank=True, null=True)

  def __str__(self):
    return u'%s' % (self.name)

class RuleColTemplate(RuleCollection):
  num_users = models.IntegerField()

class Rule(models.Model):
  phrase = models.CharField(max_length=500)
  exception_phrase = models.CharField(max_length=500, blank=True, null=True)
  rule_collection = models.ForeignKey(RuleCollection, on_delete=models.CASCADE)
  case_sensitive = models.BooleanField(default=False)
  spell_variants = models.BooleanField(default=True)

  def __str__(self):
    return u'%s %s' % (self.phrase, self.rule_collection)

  def get_phrase(self):
    if (self.spell_variants):
      return variantReg(self.phrase)    
    else:
      return self.phrase      

  def get_matched_comments(self):
    channel = self.rule_collection.owner
    allComments = Comment.objects.filter(video__channel = channel)

    matched_comment_ids = []
    for comment in allComments:
      lookups = []      
      rule_phrase = self.get_phrase()
      if (self.case_sensitive):
        lookup = re.search(r'\b({})\b'.format(rule_phrase), comment.text)
      else:
        lookup = re.search(r'\b({})\b'.format(rule_phrase), comment.text, re.IGNORECASE)
      lookups.append(lookup)
      if any(lookups):
        matched_comment_ids.append(comment.id)  
    return matched_comment_ids  

  def num_matched_comments(self):
    matched_comment_ids = self.get_matched_comments()
    return len(matched_comment_ids)

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