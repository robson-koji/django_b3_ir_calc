
$(document).ready(function() {


    /* Endorsement page */
    // Initialization
    $('#data-table-endorse').DataTable( {
        "order": [[ 9, "desc" ], [ 6, "asc" ], [ 5, "asc" ]],
        "pageLength": 100
    } );
    var rowCallback;

    // Radio button change sort order
    $('input[type=radio][name=sort_endorse]').change(function() {
        if (this.value == 'sort_endorse_default') {
          var order = [[ 9, "desc" ], [ 6, "asc" ], [ 5, "asc" ]];
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
