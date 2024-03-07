var socket = io();

$("#datepicker").datepicker({
    autoclose: true,
    todayHighlight: true,
}).datepicker('update', new Date());

socket.on('rate', function(msg) {
    $('#result').html(msg["msg"]);
    $('#counter-asset-input').val(msg["answer"]);

    if (msg["error"] === true) {
        $('#result-logo').css("color", "red");
    } else {
        $('#result-logo').css("color", "green");
    }
    $('#result-div').css("display", "flex");
});

$('#date-helper').html($('#date-input').val());
$('#base-helper').html($('#normalize').val());
$('#amount-helper').html($('#base-asset-input').val());
$('#counter-helper').html($('#normalize2').val());


function readData() {
    var date = $('#date-input').val();
    var baseCcy = $('#normalize').val();
    var baseAmt = $('#base-asset-input').val();
    var counterCcy = $('#normalize2').val();
    return {
        "date": date,
        "baseCcy": baseCcy,
        "baseAmt": baseAmt,
        "counterCcy": counterCcy
    }
}


function submitBtn() {
    let data = readData();
    socket.emit("click", data)
    $('#result-div').css("display", "none");
}


function updateHelper(id, value) {
    if (id === 'normalize') {
        $('#base-helper').html(value);
    } else if (id === 'normalize2') {
        $('#counter-helper').html(value);
    } else if (id == 'date-input') {
        $('#date-helper').html(value);
    } else {
        $('#amount-helper').html(value);
    }
}