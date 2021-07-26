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
    'loadFilters': 'GET',
    'charts/overview': 'GET',
    'charts/filter/*/overview': 'GET',
    'charts/filter/*/rule/*': 'GET'
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

  WordFilterApiRequest.prototype._getRequestMethod = function () {
    for (var action in ACTIONS) {
      if (this._action === action) {
        return 'GET';
      } else {
        var srcChunks = action.split('/'),
          curChunks = this._action.split('/');
        if (curChunks.reduce(function (acc, cur, i) {
            return acc && (i < srcChunks.length) &&
              (srcChunks[i] === cur || srcChunks[i] === '*');
          }, true)) {

          return 'GET';
        }
      }
    }
    return 'POST';
  }

  WordFilterApiRequest.prototype.execute = function () {
    // Decide whether there can be a body for the request
    var method = this._getRequestMethod();
    if (typeof this._body !== 'undefined' &&
      this._body !== null && method === 'GET') {

      return Promise.reject(new Error('Tried to invoke GET endpoint with body'));
    }
    var config = {
      'method': method,
      'headers': {}
    };

    if (typeof this._body !== 'undefined' && this._body !== null) {
      config['body'] = JSON.stringify(this._body);
      config.headers['Content-Type']= 'application/json';
    }
    return fetch(END_POINT + '/' + this._action, config).then(function (resp) {
      if (!resp.ok) {
        return resp.text().then(function (message) {
          throw new Error(resp.status + ': ' + message);
        });
      } else {
        return resp.json();
      }
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

  LocalDb.prototype.delete = function (key) {
    delete this._db[key];
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

  WordFilterApi.prototype.getUserInfo = function () {
    if (this._mode === 'local-only') {
      return new FakeApiRequest({
        'name': 'Local Debug Channel',
        'channel_id': 'THIS_IS_NOT_A_REAL_ID'
      });
    } else {
      return this.createRequest('authenticate');
    }
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
      return this.createRequest('loadFilters');
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
      return this.createRequest('createFilter', {
        'name': name,
        'reference': reference
      });
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
      return this.createRequest('updateFilter', {
        'id': id,
        'updateAction': key,
        'updateValue': item
      });
    }
  };

  WordFilterApi.prototype.removeFilter = function (id) {
    // there is no id yet so
    if (this._mode === 'local-only') {
      this._db.delete(id);
      return new FakeApiRequest({});
    } else {
      return this.createRequest('deleteFilter', {
        'id': id
      });
    }
  };

  WordFilterApi.prototype.getRuleExamples = function (parentId, data, limit) {
    if (this._mode === 'local-only') {
      return new FakeApiRequest({'comments': []});
    } else {
      return this.createRequest('previewRule', {
        'id': parentId,
        'rule': data,
        'limit': limit
      });
    }
  };

  WordFilterApi.prototype.getChartMetadata = function (endpoint) {
    if (this._mode === 'local-only') {
      return new FakeApiRequest({});
    } else {
      return this.createRequest('charts/' + endpoint);
    }
  }
  exports.WordFilterApi = WordFilterApi;
});
