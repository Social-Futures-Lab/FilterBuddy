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
      require('InteractiveChart'),
      require('InteractiveTable'));
  } else {
    factory(root,
      root.dfc,
      root.Pettan,
      root.WordFilterModel,
      root.WordFilterApi,
      root.InteractiveDataTable,
      root.InteractiveChart,
      root.InteractiveTable);
  }
})(this, function (exports,
    _,
    Pettan,
    WordFilterModel,
    WordFilterApi,
    InteractiveDataTable,
    InteractiveChart,
    InteractiveTable) {

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

    this._tablePreview = null;
    this._tableRules = null;
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
    // Add the channel name
    $('nav-channel-name').innerText = userInfo.name;


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

    // Setup the tables
    this._tablePreview = new InteractiveTable($('table-preview'), [
      'actions',
      'comment',
      'author',      
      'video',      
      'time'
    ], (function (src, col) {
      if (col === 'actions') {
        return null;
      } else if (col === 'comment') {
        return src['text'];
      } else if (col === 'author') {
        return src['author'];        
      } else if (col === 'video') {
        return _('a', {
          'href': 'https://www.youtube.com/watch?v=' + src['video_id']
        }, src['video_title']);
      } else if (col === 'time') {
        return src['pub_date'];
      } else {
        return null;
      }
    }).bind(this));

    this._tableRules = new InteractiveTable($('table-rules'), [
      'actions',
      'phrase',
      'case_sensitive',
      'spell_variants',
      'caught_comments'
    ], (function (src, col) {
      if (col === 'actions') {
        var delButton = _('a', {
          'className': 'btn btn-danger',
          'href': '#'
        }, _('i', {'className': 'bi bi-trash'}));
        delButton.addEventListener('click', (function (e) {
          e.preventDefault();
          src.delete().then((function () {
            this._tableRules.removeRows(function (r) { return r === src; });
          }).bind(this)).catch(function (e) {
            alert('Delete filter rule failed with: ' + e)
          });
        }).bind(this));
        return delButton;

      } else if (col === 'phrase') {
        return src.toString();

      } else if (col === 'case_sensitive') {
        var initClassName;
        if (src.getCaseSensitive() === true){
          initClassName = 'btn btn-toggle active';
        }
        else {
          initClassName = 'btn btn-toggle';
        }
        var checkboxButton = _('button', {
          'type': 'button',
          'className': initClassName,
          'data-toggle': 'button',
          'aria-pressed': 'true',
          'autocomplete': 'off',          
        }, _('div', {'className': 'handle'}));
        checkboxButton.addEventListener('click', (function (e){
          e.preventDefault();                      
          src.setCaseSensitive().then((function (new_case_sensitive) {
            if (new_case_sensitive === true){
              checkboxButton.className = 'btn btn-toggle active';
            }
            else if (new_case_sensitive === false){
              checkboxButton.className = 'btn btn-toggle';
            }
          }).bind(this)).catch(function (e) {
            alert('Update case sensitive checkboxButton for rule failed with: ' + e)
          });
        }).bind(this));                               
        return checkboxButton;

      } else if (col === 'spell_variants') {
        var initClassName;
        if (src.getSpellVariants() === true){
          initClassName = 'btn btn-toggle active';
        }
        else {
          initClassName = 'btn btn-toggle';
        }
        var checkboxSpellButton = _('button', {
          'type': 'button',
          'className': initClassName,
          'data-toggle': 'button',
          'aria-pressed': 'true',
          'autocomplete': 'off',          
        }, _('div', {'className': 'handle'}));
        checkboxSpellButton.addEventListener('click', (function (e){
          e.preventDefault();                      
          src.setSpellVariants().then((function (new_spell_variants) {
            if (new_spell_variants === true){
              checkboxSpellButton.className = 'btn btn-toggle active';
            }
            else if (new_spell_variants === false){
              checkboxSpellButton.className = 'btn btn-toggle';
            }
          }).bind(this)).catch(function (e) {
            alert('Update spell variants checkboxButton for rule failed with: ' + e)
          });
        }).bind(this));                               
        return checkboxSpellButton;        

      } else if (col === 'caught_comments') {      
        const matched_comments = src.getNumMatchedComments()
        console.log(matched_comments);
        return matched_comments.toString();
      } else {
        return null;
      }
    }).bind(this));

    // Bind some GUI elements
    // = Binding for filter name setup
    this._P.bind($('filter-name'), 'input', 'gui.filter-name.change');
    this._P.listen('gui.filter-name.change', (function (e) {
      var currentFilter = this._sidebar.selected();
      if (currentFilter === null) {
        throw new Error('Name changed but nothing selected!');
      }
      return currentFilter.setName(e.target.innerText).then((function () {
        this._P.emit('sidebar.update.labels');
      }).bind(this))
    }).bind(this));

    // Previewing caught comments when adding a new rule
    this._P.bind($('rule-explore'), 'keyup', 'gui.rule.preview.change');
    this._P.bind($('rule-explore'), 'change', 'gui.rule.preview.change');
    this._P.listen('gui.rule.preview.change', (function (e) {
      var currentFilter = this._sidebar.selected();
      if (currentFilter === null) {
        throw new Error('Illegal state. Cannot preview rule with no filter.');
      }
      // Get the phrase
      var phrase = e.target.value.trim();
      currentFilter.previewRule().setPhrase(phrase);
      return this._P.emit('comments.preview', currentFilter);
    }).bind(this));

    this._P.listen('comments.preview', (function (filter) {
      if (filter.previewRule().getPhrase().length > 0) {
        return filter.previewRule().preview().then((function (comments) {
          $('label-preview-mode').innerText = 'The table below shows the comments that are matched by the word "' +
            filter.previewRule().toString() + '"';
          this._tablePreview.setRows(comments['comments']);
        }).bind(this));
      }
      else {
        $('label-preview-mode').innerText = '';
        this._tablePreview.setRows([]);
      } 
    }).bind(this));

    this._P.bind($('btn-add-rule'), 'click', 'gui.rule.add');
    this._P.listen('gui.rule.add', (function (e) {
      // The add rule button was clicked
      e.preventDefault();

      var currentFilter = this._sidebar.selected();
      if (currentFilter === null) {
        throw new Error('Illegal action. Cannot add rule to no filter.')
      }

      if (currentFilter.previewRule().getPhrase().length === 0) {
        return; // Nothings
      }

      return currentFilter.finalizePreviewRule().then((function () {
        // Trigger both an update in the rules list and an update for the chart
        $('rule-explore').value = '';
        return Promise.all([
          this._P.emit('dataTables.load.filter', currentFilter),
          this._P.emit('charts.draw.filter', currentFilter),
          this._P.emit('rules.preview', currentFilter)
        ]);
      }).bind(this));
    }).bind(this));
    this._P.listen('rules.preview', (function (item) {
      var currentFilter = (typeof item !== 'undefined') ?
        item :
        this._sidebar.selected();
      if (currentFilter !== null) {
        this._tableRules.setRows(currentFilter.getRules());
      }
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
        return this._P.emit('sidebar.update').then((function () {
          this._sidebar.select(function (item) {
            return item.getId() === id;
          });
        }).bind(this));
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
          // Viewing some group      

          $('filter-name').innerText = group.getName();
          $('name-wrapper').className = !group.isFinalized() ?
            'name-wrapper default' : 'name-wrapper';
          if (!group.isFinalized()) {
            // Viewing the add group group
            this._filterEditorTabs.showOnly(['new']);
            $('btn-delete').style.display = 'none';
          } else {
            // Viewing existing group
            $('rule-explore').value = ''; // should trigger a preview
            this._filterEditorTabs.showOnly(['preview', 'edit']);
            $('btn-delete').style.display = '';

            return Promise.all([
              this._P.emit('dataTables.load.filter', group),
              this._P.emit('charts.draw.filter', group),
              this._P.emit('rules.preview', group),
              this._P.emit('comments.preview', group)
            ]);
          }
        }
      } else {
        // Overview tab
        this._tabs.showOnly(['filter-overview']);
        this._sidebarOverview.className =
          'list-group-item list-group-item-action active';
        this._P.emit('dataTables.load.overview');
        return this._P.emit('charts.draw.overview');
      }
    }).bind(this));

    this._P.listen('dataTables.load.filter', (function (filter) {
      var dataTable = new InteractiveDataTable(this._model);
      return dataTable.drawCommentTableData(filter.getId());
    }).bind(this));

    this._P.listen('dataTables.load.overview', (function () {
      var dataTable = new InteractiveDataTable(this._model);
      return dataTable.drawAllCommentsTableData();
    }).bind(this));    


    this._P.listen('charts.draw.filter', (function (filter) {
      var chart = new InteractiveChart($('chart-filter-container'), this._api);
      return chart.drawFilterGroup(filter.getId());
    }).bind(this));

    this._P.listen('charts.draw.overview', (function () {
      var chart = new InteractiveChart($('chart-overview-container'),
        this._api);
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
