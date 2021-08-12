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

  function pipeKeywords(myList){
    const myNewList = [];
    for (var i = 0; i < myList.length; i++) {
      var elem = "\\b" + myList[i] + "\\b";
      myNewList.push(elem);
    }
    var output = myNewList.join('|');
    return output;
  }  

  function highlight(data, phrases) {
    var innerHTML = '<span>' + data + ' </span>';

    var textD = pipeKeywords(phrases);
    var textPattern = new RegExp(textD, 'i');
    var match = textPattern.exec(data);
    if (match){
      const index = match.index + 6;
      innerHTML = innerHTML.substring(0,index) + "<span class='highlight'>" + innerHTML.substring(index,index+match[0].length) + "</span>" + innerHTML.substring(index + match[0].length);        
    } 
    return innerHTML;
  }  

  function InteractiveDataTable(model) {
    this._model = model;
    const all_phrases = [];
    this._model.getGroups().forEach(function (group) {
      if (group.getId().length > 0){
        group.getRules().forEach(function (rule) {
          all_phrases.push(rule._phrase_regex);
        })
      }
    })
    this._all_phrases = all_phrases;
  };

  InteractiveDataTable.prototype.drawAllCommentsTableData = function(){    
    const all_phrases = this._all_phrases;    
    if ( $.fn.dataTable.isDataTable( '#recent_comments_table' ) ) {
        $('#recent_comments_table').DataTable().destroy();
    }        

    $('#recent_comments_table').DataTable({
      'serverSide': true,
      'order': [[2, "desc"]],
      'ajax': "/capi/allCommentTables" + "/?format=datatables",
      'columns': [
        {
          'data': 'text',
          'render': function (data){
            return highlight(data, all_phrases);
          }          
        },
        {'data': 'author'},
        {'data': 'pub_date'},
        {
          'data': 'video.url_id_and_title',
          'searchable': false,
          'render': function (data){
            return '<a href="https://www.youtube.com/watch?v=' + data[0] + '">' + data[1] + ' </a>';
          }          
        },
        {
          'data': 'caught_by_collection',
          'searchable': false,
        },
      ],
      "columnDefs": [
          { "orderable": false, "targets": [3, 4] }
      ],
    });    
  }

  InteractiveDataTable.prototype.drawCommentTableData = function (filter_id) {
  	if ( $.fn.dataTable.isDataTable( '#albums' ) ) {
  	    $('#albums').DataTable().destroy();
  	}

    const group_phrases = []
    this._model.getGroups().forEach(function (group) {      
      if (group.getId() === filter_id){
        group.getRules().forEach(function (rule) {
          group_phrases.push(rule._phrase_regex);
        })
      }    
    });    

    $('#albums').DataTable({
      'serverSide': true,
      'order': [[2, "desc"]],
      'ajax': "/capi/commentTables/" + filter_id + "/?format=datatables",
      'columns': [
        {
          'data': 'text',
          'render': function (data){
            return highlight(data, group_phrases);
          }          
        },
        {'data': 'author'},
        {'data': 'pub_date'},
        {
          'data': 'video.url_id_and_title',
          'searchable': false,
          'render': function (data){
            return '<a href="https://www.youtube.com/watch?v=' + data[0] + '">' + data[1] + ' </a>';
          }
        },
      ],
      "columnDefs": [
          { "orderable": false, "targets": [3] }
      ],      
    });  	
   
  };

  exports.InteractiveDataTable = InteractiveDataTable;
});
