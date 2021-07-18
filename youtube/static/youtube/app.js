"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports',
      'dfc',
      'WordFilterModel',
      'WordFilterApi',
      'Pettan'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports,
      require('dfc'),
      require('WordFilterModel'),
      require('WordFilterApi'),
      require('Pettan'));
  } else {
    factory(root,
      root.dfc,
      root.WordFilterModel,
      root.WordFilterApi,
      root.Pettan);
  }
})(this, function (exports, _, WordFilterModel, WordFilterApi, Pettan) {
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

  ListManager.prototype.selected = function () {
    return this._selected !== null ? this._selected.item : null;
  }

  function $(e) {
    return document.getElementById(e);
  }

  function App() {
    this._model = new WordFilterModel(new WordFilterApi('local-only'));
    this._P = new Pettan();
    this._tabs = new TabManager();
    this._filterEditorTabs = new TabManager();
    this._sidebar = null;
  }

  App.prototype._onLoad = function () {
    // Build the tab interface
    this._tabs.addTab('filter-editor', $('filter-editor'));

    this._filterEditorTabs.addTab('preview', $('wrap-preview'));
    this._filterEditorTabs.addTab('edit', $('wrap-edit-existing'));
    this._filterEditorTabs.addTab('new', $('wrap-create-from-scratch'));

    // Setup the sidebar
    this._sidebar = new ListManager($('filter-list'), (function (item) {
      this._P.emit('sidebar.select', item !== null ? item.getId() : null);
    }).bind(this));
    this._sidebar.load(this._model.getGroups());

    // Bind some GUI elements
    this._P.bind($('filter-name'), 'input', 'gui.filter-name.change');
    this._P.listen('gui.filter-name.change', (function (e) {
      if (this._sidebar.selected() === null) {
        throw new Error('Name changed but nothing selected!');
      }
      var currentId = this._sidebar.selected().getId();
      var currentFilter = this._model.getGroup(currentId);
      currentFilter.setName(e.target.innerText);
    }).bind(this));
    this._P.bind($('btn-create-rule-group'), 'click', 'gui.filter.create');
    this._P.listen('gui.filter.create', (function (e) {
      // Can only be clicked in the case where it is new
      return this._model.finalizeNew('empty').then((function () {
        this._model._reshiftNewGroup();
        return this._P.emit('sidebar.update');
      }).bind(this)).catch(function (e) {
        alert(e);
        throw e;
      });
    }).bind(this));

    // Register listeners
    this._P.listen('sidebar.update', (function () {
      // Find what was selected
      var selectedId = this._sidebar.selected() !== null ?
        this._sidebar.selected().getId() : '';
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
        $('wizModeClone').setAttribute('disabled', 'disabled');
        dropdown.setAttribute('disabled', 'disabled');
      } else {
        $('wizModeClone').removeAttribute('disabled');
        dropdown.removeAttribute('disabled');
      }
    }).bind(this));

    this._P.listen('sidebar.select', (function (item) {
      if (item !== null) {
        var group = this._model.getGroup(item);
        if (group !== null) {
          // Set the head text
          $('filter-name').innerText = group.getName();
          if (group.getId() === '') {
            this._filterEditorTabs.showOnly(['new']);
          } else {
            this._filterEditorTabs.showOnly(['preview', 'edit']);
          }
        }
      }
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
