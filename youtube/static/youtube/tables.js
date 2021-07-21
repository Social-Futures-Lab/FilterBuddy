"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'dfc'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports, exports.dfc);
  } else {
    factory(root, root.dfc);
  }
})(this, function (exports, _) {
  function InteractiveTable(dom, rows) {
    this._dom = dom;
    this._rows = rows;

    // Find the body
    var body = dom.getElementsByTagName('tbody');
    if (body.length < 1) {
      throw new Error('Could not find table body');
    }
    this._body = body[0];
  }

  InteractiveTable.prototype.loadRows = function () {

  };

  exports.InteractiveTable = InteractiveTable;
});
