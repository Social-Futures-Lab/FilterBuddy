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

  function $(e) {
    return document.getElementById(e);
  }

  function App() {
    this._api = new WordFilterApi();
    this._model = new WordFilterModel(this._api);
    this._P = new Pettan();

    this._groups = [];
    this._currentGroup = null;

    this._tablePreview = null;
    this._tableRules = null;
  }

  App.prototype._onLoad = function () {
    this._api.getUserInfo().execute().catch(function (e) {
      // Probably not logged in
      if (window.location.search.indexOf('debug') < 0) {
        // Dont do anything
      }
    }).then((function (userInfo) {
      this._bind(userInfo);
    }).bind(this));
  };

  App.prototype._bind = function (userInfo) {
    // Add the channel name
    $('nav-channel-name').innerText = userInfo.name;

    // Setup the tables
    this._tablePreview = new InteractiveTable($('table-preview'), [
      'actions',
      'comment',
      'author',
      'video',
      'time',
      'caught_by',
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
      } else if (col === 'caught_by') {
        return src['catching_collection'];        
      } else {
        return null;
      }
    }).bind(this));

    this._tableRules = new InteractiveTable($('table-rules'), [
      'actions',
      'phrase',
      'case_sensitive',
      'spell_variants',
      'caught_comments',
      'rule_action',
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
        const matched_comments = src.getNumMatchedComments();
        return matched_comments.toString();
      } else if (col === 'rule_action') {    
        // var actionDropdownButton = _('button', {
        //   'type': 'button',
        //   'className': "btn btn-secondary dropdown-toggle",
        //   'id': "dropdownMenuButton1",
        //   'data-bs-toggle': 'dropdown',
        //   'aria-expanded': 'false',
        // }, _('span', {
        //   'id': 'selected', 
        //   'innerText': 'Dropdown button',
        //   })
        // );
        var actionDropdownButton = "Delete";
        return actionDropdownButton;
      } else {
        return null;
      }
    }).bind(this));

    // Bind some GUI elements
    // = Binding for filter name setup
    this._P.bind($('filter-name'), 'input', 'gui.filter-name.change');
    this._P.listen('gui.filter-name.change', (function (e) {
      var currentFilter = this._currentGroup;
      return currentFilter.setName(e.target.innerText).then((function () {
        this._P.emit('sidebar.update.labels');
      }).bind(this))
    }).bind(this));

    // Previewing caught comments when adding a new rule
    this._P.bind($('rule-explore'), 'keyup', 'gui.rule.preview.change');
    this._P.bind($('rule-explore'), 'change', 'gui.rule.preview.change');
    this._P.listen('gui.rule.preview.change', (function (e) {
      var currentFilter = this._currentGroup;
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
          $('label-preview-mode').innerHTML = 'The table below shows the comments that are matched by the word "' +
            filter.previewRule().toString() + '"' + '. <span style="background-color:yellow;">Adding this rule will catch <b>' + comments['num_new_matches'].toString() + "</b> new comments. </span>";
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

      var currentFilter = this._currentGroup;
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
        this._currentGroup;
      if (currentFilter !== null) {
        this._tableRules.setRows(currentFilter.getRules());
      }
    }).bind(this));

    this._P.bind($('btn-delete'), 'click', 'gui.filter.delete');
    this._P.listen('gui.filter.delete', (function (e) {
      var selected = this._currentGroup;
      if (selected !== null) {
        if (confirm('Are you sure you want to delete this filter')) {
          return selected.delete().then((function () {
            window.location.assign('/overview')
          }).bind(this)).catch(function (e) {
            alert(e);
            throw e;
          })
        }
      }
    }).bind(this));

    // Register listeners
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
      this._groups = this._model.getGroups();
      // Find the current group id
      var regex = new RegExp('\\/collection\\/(.+?)\\/', 'g');
      var match = regex.exec(window.location.pathname);
      var groupId = parseInt(match[1], 10);
      this._currentGroup = this._model.getGroup(groupId + '');

      // Mimic selection
      $('rule-explore').value = '';

      return Promise.all([
        this._P.emit('dataTables.load.filter', this._currentGroup),
        this._P.emit('charts.draw.filter', this._currentGroup),
        this._P.emit('rules.preview', this._currentGroup),
        this._P.emit('comments.preview', this._currentGroup)
      ]);
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
