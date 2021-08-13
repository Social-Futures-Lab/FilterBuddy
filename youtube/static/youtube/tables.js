"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'dfc'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports, require('dfc'));
  } else {
    factory(root, root.dfc);
  }
})
(this, function (exports, _) {
  function InteractiveTable(dom, cols, rowBuilder) {
    this._dom = dom;
    this._cols = cols;
    this._rowBuilder = rowBuilder;
    this._rows = [];

    // Find the body
    var body = dom.getElementsByTagName('tbody');
    if (body.length < 1) {
      throw new Error('Could not find table body');
    }
    this._body = body[0];

    this._placeholder = _('tr', {
      'className': 'placeholder'
    }, _('td', {'colspan': this._cols.length}, 'No data'));
  }

  InteractiveTable.prototype.setRows = function (rows) {
    this.removeRows();
    this.addRows(rows);
  };

  InteractiveTable.prototype.addRows = function (rows) {
    if (!Array.isArray(rows)) {
      throw new Error('Rows must be an array');
    }
    if (this._rows.length === 0 && rows.length > 0) {
      this._body.removeChild(this._placeholder);
    }
    rows.forEach((function (src) {
      var row = {
        'dom': _('tr'),
        'src': src
      };
      if (src.catching_collection === null){
        row.dom.style.backgroundColor = "yellow";
      }
      this._cols.forEach((function (colName) {
        var newChildren = this._rowBuilder(src, colName);
        if (newChildren !== null) {
          row.dom.appendChild(_('td', {}, newChildren));
        } else {
          row.dom.appendChild(_('td', {}));
        }
      }).bind(this));

      this._body.appendChild(row.dom);
      this._rows.push(row);
    }).bind(this));
  };

  InteractiveTable.prototype.removeRows = function (filterFn) {
    var toRemove = (typeof filterFn === 'function') ?
      this._rows.filter(function (row) { return filterFn(row.src); }) :
      this._rows;
    // Unhook the doms
    toRemove.forEach((function (row) {
      this._body.removeChild(row.dom);
    }).bind(this));
    // Remove them from the list
    this._rows = (typeof filterFn === 'function') ?
      this._rows.filter(function (row) { return toRemove.indexOf(row) < 0; }) :
      [];
    // Do some magic to set the empty table placeholder
    if (this._rows.length === 0) {
      this._body.appendChild(this._placeholder);
    }
  };

  InteractiveTable.prototype.rerender = function (rows) {

  };

  exports.InteractiveTable = InteractiveTable;
});
