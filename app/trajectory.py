import os

from flask import Flask, request, jsonify
from flask import render_template, abort, send_file
from flask_bootstrap import Bootstrap
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from upload_forms import MILIGUploadForm, CAMSUploadForm, RMSJSONUploadForm
from wmpg_trajectory_form_solver import WMPGTrajectoryFormSolver

app = Flask(__name__)
Bootstrap(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

app.config['TEMP_DIR'] = os.path.join(app.root_path, 'static', 'temp_data')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.before_first_request
def init():
    app.config['FORMS'] = {
        "MILIG": MILIGUploadForm,
        "CAMS": CAMSUploadForm,
        "RMSJSON": RMSJSONUploadForm
    }


@app.route('/trajectory/', methods=['GET'])
def trajectory():
    milig_form = MILIGUploadForm()
    cams_form = CAMSUploadForm()
    rmsjson_form = RMSJSONUploadForm()

    return render_template('index.html', forms={"milig": milig_form, "cams" : cams_form, "rmsjson" : rmsjson_form})


@app.route('/trajectory/api', methods=['POST'])
@limiter.limit("20 per hour")
def trajectory_api():
    request_url = request.url
    format = request.values['format']

    forms = app.config.get('FORMS')
    form = forms[format]()

    if form.validate_on_submit():
        try:
            solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
        except Exception as e:
            print(e)
            abort(400)
        else:
            try:
                return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))
            except Exception as e:
                print(e)
                response = jsonify(data=str(e))
                response.status_code = 400
                return response

    response = jsonify(data=form.errors)
    response.status_code = 400
    return response


@app.route('/trajectory/temp/<uuid>/<filename>', methods=['GET'])
def load_temp_data(uuid, filename):
    file_path = os.path.join(app.config.get('TEMP_DIR'), uuid, filename)
    try:
        return send_file(file_path)
    except:
        return abort(404)

