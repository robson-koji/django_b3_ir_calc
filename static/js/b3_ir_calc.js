
/*
Using Multiple JavaScript Onload Functions
Unfortunately, you cannot place multiple onload events on a single page. You can nest multiple functions within the one onload call, but what if you need to cascade an onload script across multiple pages, some which may already have an existing onload event? use the addLoadEvent function below.
http://www.brefere.com/fbapps/bcom.nsf/cvbdate/D514491209EE5C848725801A0074AE6E?opendocument#:~:text=Unfortunately%2C%20you%20cannot%20place%20multiple,have%20an%20existing%20onload%20event%3F
*/
function addLoadEvent(func) {
	var oldonload = window.onload;
	if (typeof window.onload != 'function') {
		window.onload = func;
	} else {
		window.onload = function() {
			if (oldonload) {
				oldonload();
			}
			func();
		}
	}
}
addLoadEvent(activate_icons);

try{
  addLoadEvent(gather_stocks);
}catch(e){
}
try{
  addLoadEvent(upld_stock_sbmt_form);
}catch(e){
}



// Add onblur event to change technical analysis
$(document).ready(function() {
  $('.max_min').on('blur', function() {
     gather_stocks()
   })
});




$(document).ready(function() {
	/* Endorsement page */
	// Initialization
	$('#data-table-endorse').DataTable( {

		// Filter column - Just add column bellow to add filter.
		initComplete: function () {
				this.api().columns([3,10]).every( function () {
				// this.api().columns().every( function () {
						var column = this;
						var select = $('<select><option value=""></option></select>')
								.appendTo( $(column.header()).empty() )
								.on( 'change', function () {
										var val = $.fn.dataTable.util.escapeRegex(
												$(this).val()
										);

										column
												// .search( val ? '^'+val+'$' : '', true, false )
												.search( val ? val : '', true, false )
												.draw();
								} );

						column.data().unique().sort().each( function ( d, j ) {
								// Coluna indice, qdo tem mais de um indice, pula.
								if (column[0]==3 && /\s/g.test(d)){ return }
								select.append( '<option value="'+d+'">'+d+'</option>' )
						} );
				} );
		},

        "order": [[ 14, "desc" ], [ 11, "asc" ], [ 10, "asc" ]],
        "pageLength": 100,

				/* Show hide columns */
				dom: 'Bfrtip',
        buttons: [
            {
                extend: 'colvisGroup',
                text: 'BTC/Termo - Show',
                show: [ 4,5,6 ],
                hide: [  ]
            },
            {
                extend: 'colvisGroup',
                text: 'BTC/Termo - Hide',
                show: [ ],
                hide: [ 4,5,6]
            },
            {
                extend: 'colvisGroup',
                text: 'Show all',
                show: ':hidden'
            }
        ]
    } );
    var rowCallback;

    // Radio button change sort order
    $('input[type=radio][name=sort_endorse]').change(function() {
        if (this.value == 'sort_endorse_default') {
          var order = [[ 14, "desc" ], [ 11, "asc" ], [ 10, "asc" ]];
        }
        else if (this.value == 'sort_endorse_1') {
          var order = [[ 9, "asc" ]];
          var rowCallback = function( row, data, index ) {
            if (! data[11]){
                $(row).hide();
            }
          };
        }

        $('#data-table-endorse').DataTable( {
            destroy:true,
            "order": order,
            "pageLength": 100,
            "rowCallback": rowCallback
        } );
    });

} );
