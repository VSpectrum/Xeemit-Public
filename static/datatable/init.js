$(document).ready(function() {

	var tables = window.DataTables = {};

	$('table').each(function (){
		var table = $(this);

		if (table.attr('data-table') && table.attr('data-table').toLowerCase() == "true") {

			var limit = table.attr('data-limit') ? table.attr('data-limit') : 20;
			var tableId = table.attr('id');

			tables[tableId] = table.DataTable({
				"lengthMenu": [[Number(limit), -1], ["Page", "All"]],
				"initComplete": function () {
					this.api().columns().every(function () {
						var column = this;
						var type = $(column.footer()).attr('data-search')? $(column.footer()).attr('data-search').toLowerCase() : null;
						var bindTo = $(column.footer()).attr('data-bind');

						if (bindTo) table.find("tfoot").hide();

						switch (type) {
							case 'text':
								var title = $(column.footer()).text();
                                var input = $('<input/>', {type: "text", class:"form-control input-sm", style:"display:inline-block", placeholder:"Search " + title });

								if (bindTo) {
									$(bindTo).append(input);
									$(column.footer()).empty()
								} else {
									$(column.footer()).empty().append(input);
								}

                                input.on( 'keyup change', function () {
                                    if ( column.search() !== this.value ) {
                                        column
                                            .search( this.value )
                                            .draw();
                                    }
                                });
								break;
							case 'option':
								var appendTo = bindTo ? $(bindTo) : $(column.footer()).empty();
								var select = $('<select class="form-control input-sm" style="display:inline-block"><option value=""></option></select>')
									.appendTo(appendTo)
									.on('change', function () {
										var val = $.fn.dataTable.util.escapeRegex(
											$(this).val()
										);

										column
											.search(val ? '^' + val + '$' : '', true, false)
											.draw();
									});

								column.data().unique().sort().each(function (d, j) {
									select.append('<option value="' + d + '">' + d + '</option>')
								});
								break;
							default:
								$(this).empty();
								break;
						}
					});
				}
			});

			if (tables[tableId]) {
				tables[tableId].colTypes = table.find("data-type")
				tables[tableId].rowAdd = function (data, index) {
					var context = this;

					return context.row.add($.map(data, function (a, index) {
						switch ($(context.column(index).header()).attr("data-type")) {
							case 'boolean' :
								return a ? "True" : "False";
							case 'number' :
								return a ? a : 0;
							default:
								return a == null || a === undefined ? "" : a;
						}
					}));
				};
			}
		}
	});
});



var DataTable = (function () {
	var panel, table, search;
	
	var datatable = function (options) {

		this.options = options.advanced ? options.advanced : {};

		this.tableId = guid();
		this.target = $(options.target);
		this.title = options.title;
		this.headings = [];
		this.searchTarget = options.search;

		this.options.ajax = options.ajax;
		this.options.columns = [];

		var dataSrc = this.options.dataSrc ? this.options.dataSrc : "data";
		var self = this;
		$.each(options.columns, function (key, value) {
			self.headings.push(key);
			self.options.columns.push({data: value});
		});

		generate(this.tableId, this.title, this.headings);
	};


	var guid = function() {
	  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
		  var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
		  return v.toString(16);
	  });
	};

	var generate = function (tableId, title, headings) {
		panel = $('<div/>', {class: 'panel panel-default'});
		table = $('<table/>', { id:tableId, class:"display table table-bordered table-hover", cellspacing:"0", width:"100%"});
		search = $('<div/>', {class: 'panel panel-default'}).append($('<div/>', {class: 'panel-body'}).append($('<form/>', {class:'form-inline'})));

		var body = $('<div/>', {class: 'panel-body'}),
			head = $('<thead/>'),
			foot = $('<tfoot/>'),
			headTitle = $('<tr/>'),
			footTitle = $('<tr/>');
			
		if (title) 
			$('<div/>', {'class': 'panel-heading', 'text': title}).appendTo(panel);

		$.each(headings, function (index, value) {
			headTitle.append($('<th/>', {'text': value}));
			footTitle.append($('<th/>', {'text': value}));
		});
		
		headTitle.appendTo(head);
		footTitle.appendTo(foot);
		head.appendTo(table);
		foot.appendTo(table);
		table.appendTo(body);
		body.appendTo(panel);

		return {panel: panel, table: table};
	}

	datatable.prototype.render = function () {
		var options = this.options;

		if(this.searchTarget)
			$(this.searchTarget).append(search);

		this.target.append(panel);
		console.log(this.options);
	    var datatable = table.DataTable(options);

		table.find('tfoot th').each(function () {
	        var title = $(this).text();
	        var searchId = guid();

	        $(this).text('#' + searchId).hide();
	        search.find('form').append( '<div class="form-group"><div class="col-md-4"><input id="' + searchId + '" type="text" class="form-control" placeholder="Search ' + title + '" /></div></div>' );
		});

	    datatable.columns().every( function () {
		    var that = this;

		    $($(this.footer()).text()).on( 'keyup change', function () {
		        if ( that.search() !== this.value ) {
		            that
		                .search( this.value )
		                .draw();
		        }
		    });
		});

		console.log(datatable);

		if (options.clickable) {
			$(this.target).on('click', 'tr', function () {
				var data = datatable.row(this).data();
				options.clickable(data);
			});
		}

		return this;
	};

	return datatable;
}());