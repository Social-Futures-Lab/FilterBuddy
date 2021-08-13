"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports);
  } else {
    factory(root);
  }
})(this, function (exports) {
  function WordFilter(api, parent, def) {
    this._api = api;
    this._parent = parent;

    this._id = (typeof def === 'undefined') ?
      '' :
      ('id' in def ? ('' + def['id']) : '');
    this._phrase = (typeof def === 'undefined') ?
      '' : def['phrase'];
    this._case_sensitive = (typeof def === 'undefined') ?
      '' : def['case_sensitive'];
    this._spell_variants = (typeof def === 'undefined') ?
      '' : def['spell_variants'];
    this._phrase_regex = (typeof def === 'undefined') ?
      '' : def['phrase_regex'];
    this._num_matched_comments = (typeof def === 'undefined') ?
      0 : def['num_matched_comments'];
  }

  WordFilter.prototype.isFinalized = function () {
    return this._id !== '';
  };

  WordFilter.prototype.finalize = function () {
    if (this.isFinalized()) {
      return Promise.reject(new Error(
        'Cannot finalize an already finalized rule'));
    } else {
      return this._api.updateFilter(
        this._parent.getId(),
        'rules:add',
        this.serialize()).execute().then((function (rule) {
          this._id = rule.id;
          this._case_sensitive = rule.case_sensitive;
          this._spell_variants = rule.spell_variants;
          this._num_matched_comments = rule.num_matched_comments;
        }).bind(this));
    }
  };

  WordFilter.prototype.setPhrase = function (phrase) {
    if (!this.isFinalized()) {
      this._phrase = phrase;
      return Promise.resolve();
    } else {
      this._phrase = phrase;
      return this._api.updateFilter(
        this._parent.getId(),
        'rules:modify',
        this.serialize()).execute();
    }
  };

  WordFilter.prototype.getPhrase = function () {
    return this._phrase;
  }

  WordFilter.prototype.getCaseSensitive = function () {
    return this._case_sensitive;
  }

  WordFilter.prototype.setCaseSensitive = function () {
    if (!this.isFinalized()) {
      this._case_sensitive = true;
      return Promise.resolve();
    } else {
      return this._api.updateRule(
        this.getId(),
        'toggle_case_sensitive').execute().
        then((function (serialized) {
          this._id = serialized.id;
          this._case_sensitive = serialized.case_sensitive;
          return this._case_sensitive;
        }).bind(this));
    }
  }

  WordFilter.prototype.getSpellVariants = function () {
    return this._spell_variants;
  }

  WordFilter.prototype.setSpellVariants = function () {
    if (!this.isFinalized()) {
      this._spell_variants = true;
      return Promise.resolve();
    } else {
      return this._api.updateRule(
        this.getId(),
        'toggle_spell_variants').execute().
        then((function (serialized) {
          this._id = serialized.id;
          this._spell_variants = serialized.spell_variants;
          return this._spell_variants;
        }).bind(this));
    }
  }

  WordFilter.prototype.getPhraseRegex = function () {
    return this._phrase_regex;
  }

  WordFilter.prototype.getNumMatchedComments = function () {
    return this._num_matched_comments;
  }

  WordFilter.prototype.getId = function () {
    return this._id;
  };

  WordFilter.prototype.preview = function (numExamples) {
    return this._api.getRulePreview(
      this._parent.getId(),
      this.serialize(),
      numExamples).execute();
  };

  WordFilter.prototype.delete = function () {
    if (!this.isFinalized()) {
      return Promise.reject(new Error('Delete only works for finalized rules'));
    }
    return this._parent.removeRule(this);
  }

  WordFilter.prototype.toString = function () {
    return this._phrase !== '' ? this._phrase : '(Empty)';
  };

  WordFilter.prototype.serialize = function () {
    return {
      'id': this._id,
      'phrase': this._phrase,
      'case_sensitive': this._case_sensitive,
      'spell_variants': this._spell_variants,
      'phrase_regex': this._phrase_regex,
      'num_matched_comments': this._num_matched_comments,
    };
  };

  function WordFilterGroup(parent, api, def) {
    this._parent = parent;
    this._api = api;

    this._id = (typeof def === 'undefined' ? '' :
      ('id' in def ? ('' + def['id']) : ''));
    this._name = (typeof def === 'undefined' ? 'Unnamed Group' : def['name']);

    this._rules = [];
    this._previewRule = new WordFilter(api, this, {'phrase': ''});

    if (typeof def !== 'undefined' && 'rules' in def) {
      this._loadRules(def['rules'])
    }
  }

  WordFilterGroup.prototype._loadRules = function (rules) {
    if (!Array.isArray(rules)) {
      this._rules = [];
    } else {
      this._rules = rules.map((function (ruleDef) {
        return new WordFilter(this._api, this, ruleDef);
      }).bind(this));
    }
  };

  WordFilterGroup.prototype.previewRule = function () {
    return this._previewRule;
  }

  WordFilterGroup.prototype.finalizePreviewRule = function () {
    return this._previewRule.finalize().then((function () {
      this._rules.push(this._previewRule);
      this._previewRule = new WordFilter(this._api, this);
    }).bind(this));
  };

  WordFilterGroup.prototype.removeRule = function (rule) {
    if (rule._parent !== this) {
      return Promise.reject(new Error('Cannot remove foreign rule'));
    }
    return this._api.updateFilter(
      this._id,
      'rules:remove',
      rule.serialize()).execute().then((function () {
        // Remove the rule locally
        this._rules = this._rules.filter(function (r) {
          return r === rule || r.getId() === rule.getId();
        });
      }).bind(this));
  };

  WordFilterGroup.prototype.isFinalized = function () {
    return this._id !== '';
  };

  WordFilterGroup.prototype.getId = function () {
    return this._id;
  };

  WordFilterGroup.prototype.toString = function () {
    if (!this.isFinalized()) {
      return '+ Add';
    } else {
      return this.getName();
    }
  };

  WordFilterGroup.prototype.getName = function () {
    return this._name;
  };

  WordFilterGroup.prototype.setName = function (newName) {
    if (this.isFinalized()) {
      return this._api.updateFilter(this._id, 'name', newName).
        execute().
        then((function () {
          this._name = newName;
        }).bind(this));
    } else {
      this._name = newName;
      return Promise.resolve();
    }
  };

  WordFilterGroup.prototype.getRules = function () {
    return this._rules.slice(0);
  };

  WordFilterGroup.prototype.preview = function () {
    if (this.isFinalized()) {
      return this._api.getGroupPreview(this._id).execute();
    } else {
      return Promise.reject(new Error('Cannot preview non-final group.'))
    }
  };

  WordFilterGroup.prototype.finalize = function (reference) {
    if (this.isFinalized()) {
      throw new Error('Cannot finalize an already final filter');
    }
    return this._api.createFilter(this._name, reference).
      execute().
      then((function (serialized) {
        this._id = serialized.id;
        this._loadRules(serialized['rules']);
        return this._id;
      }).bind(this));
  };

  WordFilterGroup.prototype.serialize = function () {
    return {
      'id': this._id,
      'name': this._name,
      'rules': this._rules.map(function (rule) {
        return rule.serialize();
      })
    }
  };

  WordFilterGroup.prototype.delete = function () {
    if (this.isFinalized()) {
      return this._api.removeFilter(this._id).execute().then((function () {
        var id = this._id;
        this._parent._setGroups(this._parent._filterGroups.filter(function (g) {
          return g.getId() !== id;
        }));
      }).bind(this));
    }
  };

  function WordFilterModel(api) {
    this._api = api;

    this._filterGroups = [];
    this._currentNew = null;

    this._setGroups([]);
  }

  WordFilterModel.prototype.load = function () {
    return this._api.loadWordFilters().execute().then((function (data) {
      this._setGroups(data.filters.map((function (def) {
        return new WordFilterGroup(this, this._api, def);
      }).bind(this)));
      if (this._currentNew === null) {
        this._reshiftNewGroup();
      }
    }).bind(this));
  }

  WordFilterModel.prototype._createNewGroup = function () {
    return new WordFilterGroup(this, this._api);
  };

  WordFilterModel.prototype._setGroups = function (groups) {
    this._filterGroups = groups.filter(function (g) {
      return g.isFinalized(); // Non-finalized items don't go into main array
    });
  };

  WordFilterModel.prototype._reshiftNewGroup = function () {
    // Make a new group and shift it into the list of groups
    if (this._currentNew !== null) {
      // Put the new thing into the list of finalized items
      this._filterGroups.push(this._currentNew);
    }
    this._currentNew = this._createNewGroup();
  }

  WordFilterModel.prototype.getGroups = function () {
    // Give a copy of the groups
    if (this._currentNew === null) {
      this._reshiftNewGroup();
    }
    return this._filterGroups.concat([this._currentNew]);
  };

  WordFilterModel.prototype.getGroup = function (id) {
    if (typeof id === 'undefined' || id === null || id === '') {
      return this._currentNew;
    }
    var candidates = this._filterGroups.filter(function (g) {
      return g.getId() === id;
    });
    return candidates.length > 0 ? candidates[0] : null;
  };

  WordFilterModel.prototype.finalizeNew = function (reference) {
    return this._currentNew.finalize(reference);
  };

  exports.WordFilterModel = WordFilterModel;
});
