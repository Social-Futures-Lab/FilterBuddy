"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports',
      'dfc',
      'WordFilterModel',
      'WordFilterApi',
      'InteractiveChart',
      'Pettan'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports,
      require('dfc'),
      require('WordFilterModel'),
      require('WordFilterApi'),
      require('InteractiveChart'),
      require('Pettan'));
  } else {
    factory(root,
      root.dfc,
      root.Pettan
      root.WordFilterModel,
      root.WordFilterApi,
      root.InteractiveChart);
  }
})(this, function (exports,
    _,
    Pettan,
    WordFilterModel,
    WordFilterApi,
    InteractiveChart) {

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
  };

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

  function ListManager(root, onSelect) {
    this._list = [];
    this._root = root;
    this._selected = null;
    this._onSelect = onSelect;
  }

  ListManager.prototype.load = function (list) {
    this._root.innerHTML = '';
    this._list = list.map((function (item) {
      var dom = _('a', {
        'className': 'list-group-item list-group-item-action',
        'href': '#'
      }, item.toString());
      dom.addEventListener('mousedown', ((function (item) {
        return function (e) {
          e.preventDefault();
          this.select(function (newItem) {
            return newItem === item;
          });
        };
      })(item)).bind(this));
      this._root.appendChild(dom);
      return {
        'dom': dom,
        'item': item
      };
    }).bind(this));
  };

  ListManager.prototype.select = function (filter) {
    var selected = this._list.filter(function (record) {
      record.dom.className = 'list-group-item list-group-item-action';
      return filter(record.item);
    });
    this._selected = selected.length > 0 ? selected[0] : null;
    if (this._selected !== null) {
      this._selected.dom.className = 'list-group-item list-group-item-action active';
    }
    if (typeof this._onSelect === 'function') {
      this._onSelect(this._selected !== null ? this._selected.item : null);
    }
  };

  ListManager.prototype.refresh = function () {
    this._list.forEach(function (item) {
      item.dom.innerText = item.item.toString();
    });
  };

  ListManager.prototype.selected = function () {
    return this._selected !== null ? this._selected.item : null;
  };

  function $(e) {
    return document.getElementById(e);
  }

  function App() {
    this._api = new WordFilterApi();
    this._model = new WordFilterModel(this._api);
    this._P = new Pettan();
    this._tabs = new TabManager();
    this._radioManager = new RadioManager();
    this._filterEditorTabs = new TabManager();
    this._sidebar = null;
    this._sidebarOverview = null;
  }

  App.prototype._onLoad = function () {
    this._api.getUserInfo().execute().then((function (userInfo) {
      this._bind(userInfo);
    }).bind(this)).catch(function (e) {
      // Probably not logged in
      if (window.location.search.indexOf('debug') < 0) {
        window.location = '/authorize';
      }
    });
  };

  App.prototype._bind = function (userInfo) {
    // Build the tab interface
    this._tabs.addTab('filter-editor', $('filter-editor'));
    this._tabs.addTab('filter-overview', $('filter-overview'));

    this._filterEditorTabs.addTab('preview', $('wrap-preview'));
    this._filterEditorTabs.addTab('edit', $('wrap-edit-existing'));
    this._filterEditorTabs.addTab('new', $('wrap-create-from-scratch'));

    // Add the radio toggles
    this._radioManager.addRadio($('wiz-mode-empty'));
    this._radioManager.addRadio($('wiz-mode-preset'), $('sec-template'));
    this._radioManager.addRadio($('wiz-mode-clone'), $('sec-existing'));

    // Setup the sidebar
    this._sidebar = new ListManager($('filter-list'), (function (item) {
      if (item === null) {
        this._P.emit('sidebar.select', null);
      } else {
        this._P.emit('sidebar.select', item.getId());
      }
    }).bind(this));
    this._sidebar.load(this._model.getGroups());
    this._sidebarOverview = $('sidebar-overview');
    this._P.bind(this._sidebarOverview, 'click', 'sidebar.select.overview');
    this._P.listen('sidebar.select.overview', (function (e) {
      e.preventDefault();
      this._sidebar.select(function () { return false; });
    }).bind(this));

    // Bind some GUI elements
    this._P.bind($('filter-name'), 'input', 'gui.filter-name.change');
    this._P.listen('gui.filter-name.change', (function (e) {
      if (this._sidebar.selected() === null) {
        throw new Error('Name changed but nothing selected!');
      }
      var currentId = this._sidebar.selected().getId();
      var currentFilter = this._model.getGroup(currentId);
      return currentFilter.setName(e.target.innerText).then((function () {
        this._P.emit('sidebar.update.labels');
      }).bind(this))
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
      return this._model.finalizeNew(mode).then((function () {
        this._model._reshiftNewGroup();
        return this._P.emit('sidebar.update');
      }).bind(this)).catch(function (e) {
        alert(e);
        throw e;
      });
    }).bind(this));
    this._P.bind($('btn-delete'), 'click', 'gui.filter.delete');
    this._P.listen('gui.filter.delete', (function (e) {
      var selected = this._sidebar.selected();
      if (selected !== null) {
        if (confirm('Are you sure you want to delete this filter')) {
          return selected.delete().then((function () {
            return this._P.emit('sidebar.update');
          }).bind(this)).catch(function (e) {
            alert(e);
            throw e;
          })
        }
      }
    }).bind(this));

    // Register listeners
    this._P.listen('sidebar.update.labels', (function () {
      this._sidebar.refresh();
      // Also update the new item dropdowns
      var dropdown = $('dropdown-existing-groups');
      for (var i = 0; i < dropdown.children.length; i++) {
        var option = dropdown.children[i];
        if (option.value && option.value.startsWith('existing:')) {
          option.innerText = this._model.getGroup(
            option.value.substring(9)).toString();
        }
      }
    }).bind(this));
    this._P.listen('sidebar.update', (function () {
      // Find what was selected
      var selectedId = this._sidebar.selected();
      this._sidebar.load(this._model.getGroups());
      this._sidebar.select(function (item) {
        return item.getId() === selectedId;
      });
      // Also update the new item dropdowns
      var dropdown = $('dropdown-existing-groups');
      dropdown.innerHTML = '';
      var added = 0;
      this._model.getGroups().forEach(function (group) {
        if (group.isFinalized()) {
          dropdown.appendChild(_('option', {
            'value': 'existing:' + group.getId()
          }, group.toString()));
          added += 1;
        }
      });
      if (added === 0) {
        $('wiz-mode-clone').setAttribute('disabled', 'disabled');
        dropdown.setAttribute('disabled', 'disabled');
      } else {
        $('wiz-mode-clone').removeAttribute('disabled');
        dropdown.removeAttribute('disabled');
      }
    }).bind(this));

    this._P.listen('sidebar.select', (function (item) {
      if (item !== null) {
        this._tabs.showOnly(['filter-editor']);
        this._sidebarOverview.className =
          'list-group-item list-group-item-action';
        var group = this._model.getGroup(item);
        if (group !== null) {
          // Set the head text
          $('filter-name').innerText = group.getName();
          $('name-wrapper').className = !group.isFinalized() ?
            'name-wrapper default' : 'name-wrapper';
          if (!group.isFinalized()) {
            this._filterEditorTabs.showOnly(['new']);
            $('btn-delete').style.display = 'none';
          } else {
            this._filterEditorTabs.showOnly(['preview', 'edit']);
            $('btn-delete').style.display = '';
          }

          if (group.isFinalized()) {
            return this._P.emit('charts.draw.filter', group);
          }
        }
      } else {
        this._tabs.showOnly(['filter-overview']);
        this._sidebarOverview.className =
          'list-group-item list-group-item-action active';
        return this._P.emit('charts.draw.overview');
      }
    }).bind(this));


    this._P.listen('charts.draw.filter', (function (filter) {
      // Draw the stuff
      var chart = new InteractiveChart($('chart-filter-container'));
      return chart.drawFilterGroup(filter.getId());
    }).bind(this));

    this._P.listen('charts.draw.overview', (function () {
      var chart = new InteractiveChart($('chart-overview-container'));
      return chart.drawOverview();
    }).bind(this));

    this._model.load().then((function () {
      this._P.emit('sidebar.update');
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
