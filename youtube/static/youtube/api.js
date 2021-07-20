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
  const END_POINT = '/api';
  const ACTIONS = {
    'get_videos': 'GET',
    'loadFilters': 'GET',
    'updateFilter': 'POST'
  }

  function FakeApiRequest(response) {
    this._response = response;
  }

  FakeApiRequest.prototype.execute = function () {
    if (this._response instanceof Error) {
      return Promise.reject(this._respose);
    }
    return Promise.resolve(this._response);
  }

  function WordFilterApiRequest(action, body) {
    this._action = action;
    this._body = body;
  }

  WordFilterApiRequest.prototype.execute = function () {
    return fetch(END_POINT, {
      'method': (this._action in ACTIONS ? ACTIONS[this._action] : 'POST'),
      'body': (typeof this._body !== 'undefined' ? JSON.stringify(this._body) : '{}'),
      'headers': {
        'Content-Type': 'application/json'
      }
    }).then(function (resp) {
      return resp.json();
    })
  }

  function LocalDb() {
    this._db = {};
    this._indexTracker = {};
  }

  LocalDb.prototype.allocateIndexedKey = function (keyPrefix) {
    if (!(keyPrefix in this._indexTracker)) {
      this._indexTracker[keyPrefix] = 0;
    }
    return this._indexTracker[keyPrefix]++;
  };

  LocalDb.prototype.put = function (key, value) {
    this._db[key] = value;
  };

  LocalDb.prototype.has = function (key) {
    return key in this._db;
  }

  LocalDb.prototype.get = function (key, defaultValue) {
    if (this.has(key)) {
      return this._db[key];
    }
    return defaultValue;
  };

  LocalDb.prototype.getAll = function (filter) {
    var candidates = [];
    for(var key in this._db) {
      if (typeof filter === 'function' && filter(key, this._db[key])) {
        candidates.push([key, this._db[key]]);
      }
    }
    return candidates;
  }

  function WordFilterApi (operationMode) {
    // Local Mode is an in-memory debugger
    this._mode = operationMode;
    if (this._mode === 'local-only') {
      this._db = new LocalDb();
    }
  }

  WordFilterApi.prototype.createRequest = function (action, body) {
    return new WordFilterApiRequest(action, body);
  };

  WordFilterApi.prototype.loadWordFilters = function () {
    //return new WordFilterApiRequest('load')
    if (this._mode === 'local-only') {
      var records = this._db.getAll().map(function (item) {
        return {
          'id': item[0],
          'name': item[1].name,
          'rules': item[1].rules
        };
      });
      return new FakeApiRequest({'filters': records});
    } else {
      throw new Error('NotImplemented: Mode ' + this._mode +
        ' not implemented');
    }
  };

  WordFilterApi.prototype.createFilter = function (name, reference) {
    // there is no id yet so
    if (this._mode === 'local-only') {
      var newKey = this._db.allocateIndexedKey('filter-group-');
      this._db.put(newKey, {
        'name': name,
        'rules': (reference === 'empty' ? [] :
          (reference.startsWith('existing:') ?
            this._db.get(reference.substring(9), {'rules': []}).rules :
            []))
      });
      return new FakeApiRequest({'id': newKey});
    } else {
      throw new Error('NotImplemented: Mode ' + this._mode +
        ' not implemented');
    }
  };

  WordFilterApi.prototype.updateFilter = function (id, key, item) {
    if (this._mode === 'local-only') {
      if (this._db.has(id)) {
        var record = this._db.get(id);
        record[key] = item;
        this._db.put(key, record);
      }
      return new FakeApiRequest({});
    } else {
      throw new Error('NotImplemented: Mode ' + this._mode +
        ' not implemented');
    }
  };

  exports.WordFilterApi = WordFilterApi;
});
