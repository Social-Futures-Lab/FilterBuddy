from .models import Channel, RuleCollection, Rule, Video, Comment, Reply

def serializeRules(collection):
  rules = Rule.objects.filter(rule_collection = collection)
  rulesList = []
  for rule in rules:
    rulesList.append({
      'id': rule.phrase,
      'phrase': rule.phrase,
      'exception_phrase': rule.exception_phrase,
    })
  return rulesList

def serializeCollection(collection):
  collectionObject = {
    'id': collection.id,
    'name': collection.name,
    'rules': serializeRules(collection),
  }
  return collectionObject
