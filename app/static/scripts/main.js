$(document).ready(function () {

});

$('.custom-file-input').on('change', function () {
    console.log("here");
    var files = [];
    for (var i = 0; i < $(this)[0].files.length; i++) {
        files.push($(this)[0].files[i].name);
    }
    $(this).next('.custom-file-label').html(files.join(', '));
});

function onFormSubmit() {

}

function setServerReturnedError() {
}

function resetInputFiles() {
}
