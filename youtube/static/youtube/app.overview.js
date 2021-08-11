"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports',
      'dfc',
      'Pettan',
      'WordFilterModel',
      'WordFilterApi',
      'InteractiveDataTable',
      'InteractiveChart'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports,
      require('dfc'),
      require('Pettan'),
      require('WordFilterModel'),
      require('WordFilterApi'),
      require('InteractiveDataTable'),
      require('InteractiveChart'));
  } else {
    factory(root,
      root.dfc,
      root.Pettan,
      root.WordFilterModel,
      root.WordFilterApi,
      root.InteractiveDataTable,
      root.InteractiveChart);
  }
})(this, function (exports,
    _,
    Pettan,
    WordFilterModel,
    WordFilterApi,
    InteractiveDataTable,
    InteractiveChart) {

  function $(e) {
    return document.getElementById(e);
  }

  function App() {
    this._api = new WordFilterApi();
    this._model = new WordFilterModel(this._api);
    this._P = new Pettan();
  }

  App.prototype._onLoad = function () {
    this._api.getUserInfo().execute().then((function (userInfo) {
      this._bind(userInfo);
    }).bind(this)).catch(function (e) {
      // Probably not logged in
      if (window.location.search.indexOf('debug') < 0) {
        window.location = '/authorized';
      }
    });
  };

  App.prototype._bind = function (userInfo) {
    // Add the channel name
    $('nav-channel-name').innerText = userInfo.name;

    this._P.listen('dataTables.load.overview', (function () {
      var dataTable = new InteractiveDataTable(this._model);
      return dataTable.drawAllCommentsTableData();
    }).bind(this));

    this._P.listen('charts.draw.overview', (function () {
      var chart = new InteractiveChart($('chart-overview-container'),
        this._api);
      return chart.drawOverview();
    }).bind(this));

    this._P.emit('dataTables.load.overview');
    this._P.emit('charts.draw.overview');
  };

  App.prototype.bind = function () {
    window.addEventListener('load', this._onLoad.bind(this));
  };

  exports.App = App;
});

// Also execute the app here;
(function (root) {
  (new root.App()).bind();
})(this);
