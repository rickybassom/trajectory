$(document).ready(function () {
    var forms = $('.upload-form');
    forms.each(function () {
        $(this).submit(function (event) {
            onFormSubmit(event, this);
        });
    });
});

$('.custom-file-input').on('change', function () {
    var files = [];
    for (var i = 0; i < $(this)[0].files.length; i++) {
        files.push($(this)[0].files[i].name);
    }
    $(this).next('.custom-file-label').html(files.join(', '));
});

// https://stackoverflow.com/questions/32811069/how-to-submit-a-flask-wtf-form-with-ajax
$.fn.serializeObject = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function onFormSubmit(event, form) {
    // Stop the browser from submitting the form.
    event.preventDefault();

    console.log('submit clicked');

    var formData = new FormData(form);
    console.log(formData);

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRFToken)
            }
        }
    });

    $.ajax({
        //more changes here
        // data: data,
        url: "/trajectory/api",
        type: "POST",
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            console.log(response);
        },
        error: function (error) {
            console.log(error);
        }
    });

}

function setServerReturnedError() {
}

function resetInputFiles() {
    // TODO
}
