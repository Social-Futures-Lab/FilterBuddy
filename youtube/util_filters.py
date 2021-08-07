from .models import Channel, RuleCollection, Rule, Video, Comment
import json

def serializeRule(rule):
  ruleObject = {
    'id': str(rule.id),
    'phrase': rule.phrase,
    'exception_phrase': rule.exception_phrase,
    'case_sensitive': rule.case_sensitive,
    'spell_variants': rule.spell_variants,
    'phrase_regex': rule.get_phrase(),
    'num_matched_comments': rule.num_matched_comments(),
  }
  return ruleObject  

def serializeRules(collection):
  rules = Rule.objects.filter(rule_collection = collection)
  rulesList = []
  for rule in rules:
    ruleObject = serializeRule(rule)
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
