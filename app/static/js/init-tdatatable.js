// ========================================================================= //
//   Table Example 1
// ========================================================================= //

// Start DataTable

let ex1 = jQuery('#example1').DataTable({});

// Delete Row Datatable

$('#example1 tbody').on('click', 'a.delet span', function () {
    ex1
        .row($(this).parents('tr'))
        .remove()
        .draw();
});


// ========================================================================= //
//   Table Example 2
// ========================================================================= //

// Hide colmun Datatable 

let ex2 = jQuery('#example2').DataTable({

    // "columnDefs": [{
    //     "targets": [3],
    //     "visible": false
    // }, {
    //     "targets": [5],
    //     "visible": false
    // }, {
    //     "targets": [8],
    //     "visible": false
    // }, {
    //     "targets": [9],
    //     "visible": false
    // }, {
    //     "targets": [10],
    //     "visible": false
    // }, {
    //     "targets": [11],
    //     "visible": false
    // }, {
    //     "targets": [12],
    //     "visible": false
    // },]
    // "columnDefs": [{
    //     "targets": [3],
    //     "visible": false
    // },]

});

// Function show modal resultat patient

$('#example2 tbody').on('click', '.vue', function () {
    // getting target row data
    var data = ex2.row($(this).parents('tr')).data();
    $('.insertHere').html(
        // Adding and structuring the full data
        // '<table class="table table-striped table-responsive-sm modalShowTable" width="100%"><tbody><tr><td>姓<td><td>' + data[1] + '</td></tr><tr><td>名<td><td>' + data[2] + '</td></tr><tr><td>邮件<td><td>' + data[3] + '</td></tr><tr><td>手机号码<td><td>' + data[4] + '</td></tr><tr><td>出生日期<td><td>' + data[5] + '</td></tr><tr><td>婚姻状况<td><td>' + data[6] + '</td></tr><tr><td>性别<td><td>' + data[7] + '</td></tr> <tr><td>血型<td><td>' + data[8] + '</td></tr> <tr><td>体重<td><td>' + data[9] + '</td></tr> <tr><td>身高<td><td>' + data[10] + '</td></tr> <tr><td>地址<td><td>' + data[11] + '</td></tr> <tr><td>病史<td><td>' + data[12] + '</td></tr></tbody></table>'
        '<table class="table table-striped table-responsive-sm modalShowTable" width="100%"><tbody><tr><td>编号<td><td>' + data[1] + '</td></tr><tr><td>姓名<td><td>' + data[2] + '</td></tr><tr><td>年龄<td><td>' + data[3] + '</td></tr><tr><td>性别<td><td>' + data[4] + '</td></tr></tbody></table>'

    );
    // calling the bootstrap modal
    $('#myModal').modal('show');

});

// Delete Row Datatable

$('#example2 tbody').on('click', '.delet', function () {
    ex2
        .row($(this).parents('tr'))
        .remove()
        .draw();
});

// ========================================================================= //
//   Table Example 3
// ========================================================================= //

// Billing List Table

var ex3 = jQuery('#example3').DataTable({
    dom: 'lrtip',
    "ordering": false,
    "bPaginate": true,
    "bInfo": true,
    "bSort": false,
    "lengthChange": false,

});

// Delete Row Datatable

$('#example3 tbody').on('click', '.delet', function () {
    ex3
        .row($(this).parents('tr'))
        .remove()
        .draw();
});

// Filter by Date inside datatable

var ex3 = $("#example3").DataTable();

minDateFilter = "";
maxDateFilter = "";

$("#daterange").daterangepicker();
$("#daterange").on("apply.daterangepicker", function (ev, picker) {
    minDateFilter = Date.parse(picker.startDate);
    maxDateFilter = Date.parse(picker.endDate);

    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        var date = Date.parse(data[1]);

        if (
            (isNaN(minDateFilter) && isNaN(maxDateFilter)) ||
            (isNaN(minDateFilter) && date <= maxDateFilter) ||
            (minDateFilter <= date && isNaN(maxDateFilter)) ||
            (minDateFilter <= date && date <= maxDateFilter)
        ) {
            return true;
        }
        return false;
    });
    ex3.draw();
});

// Select filter inside datatable

$('.table-filter-select').on('change', function () {
    ex3.search(this.value).draw();
});

// Form search inside table

$('#myInputTextField').keyup(function () {
    ex3.search($(this).val()).draw();
})
