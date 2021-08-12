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
      require('WordFilterApi'));
  } else {
    factory(root,
      root.dfc,
      root.Pettan,
      root.WordFilterModel,
      root.WordFilterApi);
  }
})(this, function (exports,
    _,
    Pettan,
    WordFilterModel,
    WordFilterApi) {

  function TabManager() {
    this._tabs = {};
  }

  TabManager.prototype.addTab = function (name, element) {
    if (!(name in this._tabs)) {
      this._tabs[name] = element;
    }
  };

  TabManager.prototype.show = function (names) {
    if (typeof names === 'string') {
      this._tabs[names].style.display = '';
    } else if (Array.isArray(names)) {
      names.forEach((function (name) {
        this._tabs[name].style.display = '';
      }).bind(this));
    }
  };

  TabManager.prototype.hide = function (names) {
    if (typeof names === 'string') {
      this._tabs[names].style.display = 'none';
    } else if (Array.isArray(names)) {
      names.forEach((function (name) {
        this._tabs[name].style.display = 'none';
      }).bind(this));
    }
  };

  TabManager.prototype.showAll = function () {
    for (var tabName in this._tabs) {
      this._tabs[tabName].style.display = '';
    }
  };

  TabManager.prototype.hideAll = function () {
    for (var tabName in this._tabs) {
      this._tabs[tabName].style.display = 'none';
    }
  };

  TabManager.prototype.showOnly = function (names) {
    this.hideAll();
    this.show(names);
  };

  TabManager.prototype.hideOnly = function (names) {
    this.showAll();
    this.hide(names);
  };

  TabManager.prototype.toggle = function (names) {
    if (typeof names === 'string') {
      this._tabs[names].style.display =
        (this._tabs[names].style.display === 'none') ?
          '' : 'none';
    } else if (Array.isArray(names)) {
      names.forEach((function (name) {
        this.toggle(name);
      }).bind(this));
    }
  };

  TabManager.prototype.hasTab = function (name) {
    return name in this._tabs;
  };

  function RadioManager() {
    this._tabManager = new TabManager();
    this._radios = [];
  }

  RadioManager.prototype._scanAndShow = function () {
    this._tabManager.hideAll();
    this._radios.forEach((function (radio) {
      var tabName = radio.name + '::' + radio.value;
      if (!this._tabManager.hasTab(tabName)) {
        return;
      }
      if (radio.checked) {
        this._tabManager.show(tabName);
      } else {
        this._tabManager.hide(tabName);
      }
    }).bind(this));
  };

  RadioManager.prototype.addRadio = function (radio, section) {
    radio.addEventListener('click', this._scanAndShow.bind(this));
    if (typeof section !== 'undefined' && section !== null) {
      this._tabManager.addTab(radio.name + '::' + radio.value, section);
    }
    this._radios.push(radio);
  };

  RadioManager.prototype.value = function () {
    return this._radios.filter(function (radio) {
      return radio.checked;
    }).map(function (radio) {
      return radio.value;
    });
  };

  function $(e) {
    return document.getElementById(e);
  }

  function App() {
    this._api = new WordFilterApi();
    this._model = new WordFilterModel(this._api);
    this._P = new Pettan();
    this._radioManager = new RadioManager();
    this._presetsTabManager = new TabManager();
  }

  App.prototype._onLoad = function () {
    this._api.getUserInfo().execute().then((function (userInfo) {
      this._bind(userInfo);
    }).bind(this)).catch(function (e) {
      // Probably not logged in
      if (window.location.search.indexOf('debug') < 0) {
        window.location.assign('/authorize');
      }
    });
  };

  App.prototype._bind = function (userInfo) {
    // Add the channel name
    $('nav-channel-name').innerText = userInfo.name;

    // Add the radio toggles
    this._radioManager.addRadio($('wiz-mode-empty'));
    this._radioManager.addRadio($('wiz-mode-preset'), $('sec-template'));
    this._radioManager.addRadio($('wiz-mode-clone'), $('sec-existing'));

    // Add the tabs
    var presetDropdown = $('dropdown-template');
    for (var i = 0; i < presetDropdown.children.length; i++) {
      var item = presetDropdown.children[i];
      var val = item.getAttribute('value');
      try {
        if (val !== null) {
          this._presetsTabManager.addTab(val, $('preview-' + val));
        }
      } catch (e) { console.err(e); }
    }
    presetDropdown.addEventListener('change', (function (e) {
      var val = e.target.value;
      this._presetsTabManager.showOnly([val]);
    }).bind(this));


    // Bind some GUI elements
    // = Binding for filter name setup
    this._P.bind($('filter-name'), 'input', 'gui.filter-name.change');
    this._P.listen('gui.filter-name.change', (function (e) {
      var currentFilter = this._model.getGroup();
      return currentFilter.setName(e.target.innerText);
    }).bind(this));

    this._P.bind($('btn-create-rule-group'), 'click', 'gui.filter.create');
    this._P.listen('gui.filter.create', (function (e) {
      // Can only be clicked in the case where it is new
      var mode = this._radioManager.value()[0];
      if (mode === 'existing') {
        mode = $('dropdown-existing-groups').value;
      } else if (mode === 'template') {
        mode = $('dropdown-template').value;
      }
      return this._model.finalizeNew(mode).then((function (id) {
        this._model._reshiftNewGroup();
        window.location.assign('/collection/' + id + '/edit')
      }).bind(this)).catch(function (e) {
        alert(e);
        throw e;
      });
    }).bind(this));

    // Register listeners
    this._model.load().then((function () {

    }).bind(this));
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
