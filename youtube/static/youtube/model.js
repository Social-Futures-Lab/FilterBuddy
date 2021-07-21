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
  function WordFilter(api, def) {
    // Current impl assumes a string for def
    if (typeof def !== 'string') {
      throw new Error('NotImplemented: Complex word filters');
    }
    this._def = def;
    this._api = api;
  }

  WordFilter.prototype.getExamples = function (numExamples) {
    return this._api;
  };

  WordFilter.prototype.toString = function () {
    return this._def;
  };

  WordFilter.prototype.serialize = function () {
    return this._def;
  };

  function WordFilterGroup(api, def) {
    this._api = api;

    this._id = (typeof def === 'undefined' ? '' : ('' + def['id']));
    this._name = (typeof def === 'undefined' ? 'Unnamed Group' : def['name']);

    this._rules = (typeof def !== 'undefined' ?
      WordFilterGroup.createRules(api, def['rules']) : []);
  }

  WordFilterGroup.createRules = function (api, rules) {
    return rules.map(function (rule) {
      return new WordFilter(api, rule);
    });
  };

  WordFilterGroup.prototype.addRule = function (rule) {
    return this._api.updateFilter(this._id, 'rule', rule).execute().
      then((function () {
        this._rules.push(rule);
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

  WordFilterGroup.prototype.getExamples = function (wordFilter) {
    // Get some examples that would be caught
    return this._api.getExamplesInContext(this._id, wordFilter);
  };

  WordFilterGroup.prototype.deleteRule = function (rule) {
    return this._api.removeRule(this._id, rule).then((function () {
      var index = this._rules.indexOf(rule);
      if (index >= 0) {
        this._rules.splice(index, 1);
      }
    }).bind(this));
  }

  WordFilterGroup.prototype.finalize = function (reference) {
    if (this.isFinalized()) {
      throw new Error('Cannot finalize an already final filter');
    }
    return this._api.createFilter(this._name, reference).
      execute().
      then((function (id) {
        this._id = id;
        return id;
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
  }

  function WordFilterModel(api) {
    this._api = api;

    this._filterGroups = null;
    this._currentNew = null;

    this._setGroups([]);
  }

  WordFilterModel.prototype.load = function () {
    return this._api.loadWordFilters().execute().then((function (data) {
      this._setGroups(data.filters.map((function (def) {
        return new WordFilterGroup(this._api, def);
      }).bind(this)));
    }).bind(this));
  }

  WordFilterModel.prototype._createNewGroup = function () {
    return new WordFilterGroup(this._api);
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
