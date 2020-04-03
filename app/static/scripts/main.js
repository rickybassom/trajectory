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

    $('#results-modal').modal('show');

    var formData = new FormData(form);

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            outputResultDiv.innerHTML = '<div class="loader"></div>';

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
            var formName = form.format.value.toLowerCase();
            if (document.getElementById("generate-plots-" + formName).checked) {
                document.getElementById("load-plots-btn").click();
            }

        },
        error: function (error) {
            outputResultDiv.innerHTML = "";
            setServerReturnedError(error, outputResultDiv);
        }
    })
    ;


}

function setServerReturnedFiles(json_data) {
    var id = json_data.id;

    var h5 = document.createElement("small");
    h5.innerText = "ID - " + id;
    outputResultDiv.appendChild(h5);

    var currentDate = new Date();
    var tenMinutesLater = new Date(currentDate.getTime() + (10 * 60 * 1000));
    executeAt(tenMinutesLater, function () {
        alert("Files " + id + "  have been removed");
    });

    var deletionTime = document.createElement("small");
    deletionTime.style.display = "block";
    deletionTime.innerText = "Files will be removed at: " + tenMinutesLater.toString();
    outputResultDiv.appendChild(deletionTime);

    for (i in json_data.files) {
        var container = document.createElement("div");

        var link = document.createElement("a");
        link.href = json_data.files[i];
        link.innerHTML = '<i class="fas fa-file"></i> ' + json_data.files[i].replace(/^.*[\\\/]/, '');
        link.setAttribute("data-toggle", "tooltip");
        link.setAttribute("title", "Download");

        container.appendChild(link);
        outputResultDiv.appendChild(container);
    }

    var btn = document.createElement("button");
    btn.id = "load-plots-btn";
    btn.classList.add("btn");
    btn.classList.add("btn-primary");
    btn.addEventListener("click", function () {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                btn.style.display = "none";
                plotBox.innerHTML = '<br><div class="loader"></div>';
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
                btn.style.display = "block";
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
    for (plot in plots) {
        plotBox.appendChild(document.createElement("hr"));

        var value = plots[plot];
        title = document.createElement("p");
        title.innerText = plot;
        plotBox.appendChild(title);

        figure = document.createElement("div");
        figure.id = "fig" + count.toString();
        figure.style.overflowX = "auto";
        plotBox.appendChild(figure);
        mpld3.draw_figure(figure.id, value);
        count = count + 1;
    }
}

function setServerReturnedError(error, box) {
    console.log(error);

    var p = document.createElement("p");
    p.innerHTML = "Error: " + error.statusText + "<br>" + error.responseText;
    box.appendChild(p);
}

function executeAt(time, func) {
    var currentTime = new Date().getTime();
    if (currentTime > time) {
        console.error("Time is in the Past");
        return false;
    }
    setTimeout(func, time - currentTime);
    return true;
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
