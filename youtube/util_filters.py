from .models import Channel, RuleCollection, Rule, Video, Comment, Reply
import json

def serializeRules(collection):
  rules = Rule.objects.filter(rule_collection = collection)
  rulesList = []
  for rule in rules:
    ruleObject = {
    'id': rule.id,
    'phrase': rule.phrase,
    'exception_phrase': rule.exception_phrase,
    }
    rulesList.append(ruleObject)
  return rulesList

def serializeCollection(collection):
  rules = serializeRules(collection)
  # rules = []
  collectionObject = {
    'id': collection.id,
    'name': collection.name,
    'rules': rules,
  }
  return collectionObject
