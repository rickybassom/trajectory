import os

from flask import Flask
from flask import render_template, abort, jsonify
from flask_bootstrap import Bootstrap


from upload_forms import MILIGUploadForm
from upload_forms import CAMSUploadForm
from upload_forms import RMSJSONUploadForm
from wmpg_trajectory_form_solver import WMPGTrajectoryFormSolver

app = Flask(__name__)
Bootstrap(app)

app.config['TEMP_DIR'] = os.path.join(app.root_path, 'static', 'temp_data')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/trajectory/', methods=['GET', 'POST'])
def trajectory():
    milig_form = MILIGUploadForm()
    cams_form = CAMSUploadForm()
    rmsjson_form = RMSJSONUploadForm()

    return render_template('index.html', milig_form=milig_form, cams_form=cams_form, rmsjson_form=rmsjson_form)

@app.route('/trajectory/api/<format>', methods=['POST'])
def trajectory_api(format):
    if format == "MILIG":
        form = MILIGUploadForm()
        if form.validate_on_submit():
            solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
            return solver.solveForZip(form, format)

        return jsonify(data=form.errors)

    elif format == "CAMS":
        form = CAMSUploadForm()
        if form.validate_on_submit():
            solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
            return solver.solveForZip(form, format)

    elif format=="RMSJSON":
        form = RMSJSONUploadForm()
        if form.validate_on_submit():
            solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
            return solver.solveForZip(form, format)

    else:
        return abort(400)
