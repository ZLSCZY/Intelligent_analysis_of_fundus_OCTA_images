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
    "columnDefs": [{
        "targets": [1],
        "visible": false
    },{
        "targets": [6],
        "visible": false
    },{
        "targets": [7],
        "visible": false
    },{
        "targets": [8],
        "visible": false
    },{
        "targets": [9],
        "visible": false
    },{
        "targets": [10],
        "visible": false
    },]

});

// Function show modal resultat patient

$('#example2 tbody').on('click', '.vue', function () {
    // getting target row data
    var data = ex2.row($(this).parents('tr')).data();
    $('.insertHere').html(
        // Adding and structuring the full data
        '<table class="table table-striped table-responsive-sm modalShowTable" width="100%"><tbody>' +
        '<tr><td>编号<td><td>' + data[2] +
        '</td></tr><tr><td>姓名<td><td>' + data[3] +
        '</td></tr><tr><td>年龄<td><td>' + data[4] +
        '</td></tr><tr><td>性别<td><td>' + data[5] +
        '</td></tr><tr><td>身高<td><td>' + data[6] +
        '</td></tr><tr><td>体重<td><td>' + data[7] +
        '</td></tr><tr><td>血型<td><td>' + data[8] +
        '</td></tr><tr><td>相关病史<td><td>' + data[9] +
        '</td></tr><tr><td>备注<td><td>' + data[10] +
        '</td></tr></tbody></table>'
    );
    // calling the bootstrap modal
    $('#myModal').modal('show');
});

$('#example2 tbody').on('click', '.vue', function () {
    // 获取目标病例的id
    var id = ex2.row($(this).parents('tr')).data()[1];
    // 用隐藏表单提交
    $('.newDiagnosis').html(
        '                    <form action="/new_diagnosis/" method="get">\n' +
        '                        <label>\n' +
        '                            <input type="hidden" name="curr_case_id" value="' + id + '">\n' +
        '                        </label>\n' +
        '                            <input type="submit" class="btn btn-info float-end" value="新增诊断">\n' +
        '                    </form>'
    );
});

$('#example2 tbody').on('click', '.vue', function () {
    // 获取目标病例的id
    var id = ex2.row($(this).parents('tr')).data()[1];
    $('.queryRecord').html(
        '                    <form action="/results/" method="get">\n' +
        '                        <label>\n' +
        '                            <input type="hidden" name="curr_case_id" value="' + id + '">\n' +
        '                        </label>\n' +
        '                            <input type="submit" class="btn btn-info float-end" value="诊断报告">\n' +
        '                    </form>'
    );
});

// update
$('#example2 tbody').on('click', '.update', function () {
    console.log(ex2.row($(this).parents('tr')).data()[1]);
    $('#update_table').html(`
    
    <div class="row">
        <div class="col-md-6">
            <div class="form-group">
                <input type="text" class="form-control" name="NPNum"
                       value="` + ex2.row($(this).parents('tr')).data()[2] + `">
            </div>
            <div class="form-group">
                <input type="text" class="form-control" name="NPName"
                       value="` + ex2.row($(this).parents('tr')).data()[3] + `">
            </div>
        </div>
        <div class="col-md-6">
            <div class="form-group">
                <input type="text" class="form-control" name="NPAge"
                       value="` + ex2.row($(this).parents('tr')).data()[4] + ` ">
            </div>
            <div class="form-group">
                <select class="form-control form-select" name="NPGender">
                    <option value="` + ex2.row($(this).parents('tr')).data()[5] + `">` + ex2.row($(this).parents('tr')).data()[5] + `</option>
                    <option value="男">男</option>
                    <option value="女">女</option>
                </select>
            </div>
        </div>
        <div class="col-md-6">
            <div class="form-group">
                <input type="text" class="form-control" name="NPHeight"
                       value="` + ex2.row($(this).parents('tr')).data()[6] + `">
            </div>
            <select class="form-control form-select" name="NPBloodType">
                <option value="` + ex2.row($(this).parents('tr')).data()[8] + `">` + ex2.row($(this).parents('tr')).data()[8] + `</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="其他">其他</option>
            </select>
        </div>
        <div class="col-md-6">
            <div class="form-group">
                <div class="form-group">
                    <input type="text" class="form-control" name="NPWeight"
                           value="` + ex2.row($(this).parents('tr')).data()[7] + `">
                </div>
                <div class="form-group">
                    <input type="text" class="form-control" name="NPNothing"
                           placeholder="空">
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-xl-12">
            <div class="form-group">
            <textarea class="form-control" name="NPCase" value="` + ex2.row($(this).parents('tr')).data()[9] + `"
                      rows="4"></textarea>
            </div>
            <div class="form-group">
            <textarea class="form-control" name="NPNote" value="` + ex2.row($(this).parents('tr')).data()[10] + `"
                      rows="4"></textarea>
            </div>
            <div class="form-group text-right">
                    <input hidden type="text" class="form-control" name="id"
                           value="` + ex2.row($(this).parents('tr')).data()[1] + `">
            </div>
        </div>
    </div>
    <button type="submit" class="btn btn-primary">保存修改</button>
`)
});

// Delete Row Datatable

$('#example2 tbody').on('click', '.delet', function () {
    console.log(ex2.row($(this).parents('tr')).data()[1]);

    var form = document.createElement("form");
    form.action = '/del_patient/';
    form.method = 'get';
    var id = document.createElement("input");
    id.type = "hidden";
    id.name = 'id';
    id.value = ex2.row($(this).parents('tr')).data()[1];
    form.appendChild(id)

    document.body.appendChild(form);
    form.submit()
    document.body.removeChild(form);

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
