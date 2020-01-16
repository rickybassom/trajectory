var outputResultDiv = $('#output-result')[0];
var forms = $('.upload-form');

$(document).ready(function () {
    forms.each(function () {
        $(this).submit(function (event) {
            onFormJSONSubmit(event, this);
        });
    });

});

function onFormJSONSubmit(event, form) {
    console.log('submit clicked');

    // Stop the browser from submitting the form.
    event.preventDefault();

    var formData = new FormData(form);

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            outputResultDiv.innerHTML = "Loading......";

            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRFToken)
            }
        }
    });

    $.ajax({
        url: "/trajectory/api",
        type: "POST",
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            outputResultDiv.innerHTML = "";
            console.log(response);
            setServerReturnedFiles(response);

        },
        error: function (error) {
            outputResultDiv.innerHTML = "";
            setServerReturnedError(error, outputResultDiv);
        }
    })
    ;


}

function setServerReturnedFiles(json_data) {
    console.log(json_data);

    var id = json_data.id;

    var h5 = document.createElement("h5");
    h5.innerText = "Files - " + id;
    outputResultDiv.appendChild(h5);

    for (i in json_data.files) {
        var link = document.createElement("a");
        link.href = json_data.files[i];

        var p = document.createElement("p");
        var filename = json_data.files[i].replace(/^.*[\\\/]/, '');
        p.innerText = filename;

        link.appendChild(p);
        outputResultDiv.appendChild(link);
    }

    var btn = document.createElement("button");
    btn.addEventListener("click", function () {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                plotBox.innerHTML = "Loading......";
            }
        });

        $.ajax({
            url: "/trajectory/temp-get-plots/" + id,
            type: "GET",
            success: function (response) {
                plotBox.innerHTML = "";
                setServerReturnedPlots(response);
            },
            error: function (error) {
                plotBox.innerHTML = "";
                setServerReturnedError(error, plotBox);
            }
        });
    });
    btn.innerText = "Plot trajectories";
    outputResultDiv.appendChild(btn);

    plotBox = document.createElement("div");
    outputResultDiv.appendChild(plotBox);
}

function setServerReturnedPlots(plots) {
    plots = JSON.parse(plots);
    var count = 0;
    for(plot in plots){
        var value = plots[plot];
        figure = document.createElement("div");
        figure.id = "fig" + count.toString();
        plotBox.appendChild(figure);
        mpld3.draw_figure(figure.id, value);
        count = count + 1;
    }
}

function setServerReturnedError(error, box) {
    console.log(error);

    var p = document.createElement("p");
    p.innerText = "Error: " + JSON.stringify(error.responseJSON);
    box.appendChild(p);
}


// add filenames chosen from file choose dialog
$('.custom-file-input').on('change', function () {
    if ($(this)[0].files.length === 0) {
        $(this).next('.custom-file-label').html("<b>Select files</b>");
        return;
    }
    if ($(this)[0].files.length === 1) {
        $(this).next('.custom-file-label').html($(this)[0].files[0].name);
        return;
    }

    if ($(this)[0].files.length > 1) {
        $(this).next('.custom-file-label').html("<b>" + $(this)[0].files.length.toString() + " selected files</b>");
    }

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
