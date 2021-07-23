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
  function InteractiveChart(dom, rows) {
    this._dom = dom;
    this._rows = rows;

    var randomColorGenerator = function () { 
	  return '#' + (Math.random().toString(16) + '0000000').slice(2, 8); 
	};

	var ctx = document.getElementById('myChart').getContext('2d');
	ctx.height = 500;
	var chart_data = JSON.parse("{{chart_data|escapejs}}");
	var chart_data_keys = Object.keys(chart_data);
	var chart_data_values = Object.values(chart_data);
	console.log("values", chart_data_keys.length);
	const myColors = [];
	for (let i=0; i < chart_data_keys.length; i++) {
	  myColors.push(randomColorGenerator());
	}                  
	var myChart = new Chart(ctx, {
	    type: 'bar',
	    data: {
	        labels: chart_data_keys,
	        datasets: [{
	            label: '# of Caught Comments',
	            data: chart_data_values,
	            backgroundColor: myColors,
	            borderColor: myColors,
	            borderWidth: 1
	        }]
	    },
	    options: {
	        // maintainAspectRatio: false,
	        scales: {
	            y: {
	                beginAtZero: true
	            }
	        }
	    }
	});
	}

  InteractiveChart.prototype.loadRows = function () {

  };

  exports.InteractiveChart = InteractiveChart;
});
