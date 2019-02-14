$(function() {
    $('#timeRangeStartDateTimePicker').datetimepicker();

    // hide the time range divs
    $('#startDateFormGroup').hide();
    $('#endDateFormGroup').hide();

    $('#inputChooseFile').on('change', function (event) {
        var fileName = event.target.files[0].name;
        $('#inputFileLabel').text(fileName);
    });

    $("input[type=radio][name=useTimeRange]").change(function () {
        if (this.value === 'yes') {
            // show the time range divs
            $('#startDateFormGroup').show();
            $('#endDateFormGroup').show();
        } else {
            $('#startDateFormGroup').hide();
            $('#endDateFormGroup').hide();
        }
    });

    $("#process").click(function() {
        window.location.href = "../views/progress.ejs";
    });
});