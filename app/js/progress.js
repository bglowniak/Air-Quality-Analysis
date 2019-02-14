$('#cancelJob').click(function () {
    window.location.href = '../views/index.ejs';
});

$(function () {
    var i = 0;
    setInterval(function () {
        if (i++ <= 10) {
            $('#progressBar').css('width', new String(i * 10) + '%');
        } else {
            window.location.href = '../views/finish.ejs';
        }
    }, 1000);
});