"use strict";

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'jQuery'], factory);
  } else if (typeof exports === 'object' && typeof exports.nodeName !== 'string') {
    factory(exports, exports.jQuery);
  } else {
    factory(root, root.jQuery);
  }
})(this, function (exports, $) {

  function InteractiveDataTable() {

  };

  InteractiveDataTable.prototype.drawCommentTableData = function (filter_id) {
	if ( $.fn.dataTable.isDataTable( '#albums' ) ) {
	    $('#albums').DataTable().destroy();
	}

    $('#albums').DataTable({
      'serverSide': true,
      'ajax': "/capi/commentTables/" + filter_id + "/?format=datatables",
      'columns': [
        {'data': 'text'},
        {'data': 'author'},
        {'data': 'pub_date'},
        {
          'data': 'video.title',
          'render': function (data){
            return '<a href="https://www.youtube.com/watch?v=' + data[0] + '">' + data[1] + ' </a>';
          }
        },
      ]
    });  	
   
  };

  exports.InteractiveDataTable = InteractiveDataTable;
});
