import os

from flask import Flask, request
from flask import render_template, abort, jsonify, send_file
from flask_bootstrap import Bootstrap
from flask_restful import Api

from upload_forms import MILIGUploadForm, CAMSUploadForm, RMSJSONUploadForm

from wmpg_trajectory_form_solver import WMPGTrajectoryFormSolver
from restful_upload_form import RestfulUploadForm

app = Flask(__name__)
api = Api(app)
Bootstrap(app)

app.config['TEMP_DIR'] = os.path.join(app.root_path, 'static', 'temp_data')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


api.add_resource(RestfulUploadForm, '/trajectory/api')


@app.route('/trajectory/', methods=['GET', 'POST'])
def trajectory():
    if request.method == 'POST':
        format = request.values['format']

        if format == "MILIG":
            form = MILIGUploadForm()
            if form.validate_on_submit():
                solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
                return solver.solve_for_zip(form, format)

            return jsonify(data=form.errors)

        elif format == "CAMS":
            form = CAMSUploadForm()
            if form.validate_on_submit():
                solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
                return solver.solve_for_zip(form, format)

            return jsonify(data=form.errors)

        elif format == "RMSJSON":
            form = RMSJSONUploadForm()
            if form.validate_on_submit():
                solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
                return solver.solve_for_zip(form, format)

            return jsonify(data=form.errors)

        else:
            return abort(400)

    milig_form = MILIGUploadForm()
    cams_form = CAMSUploadForm()
    rmsjson_form = RMSJSONUploadForm()

    return render_template('index.html', milig_form=milig_form, cams_form=cams_form, rmsjson_form=rmsjson_form)

#
# @app.route('/trajectory/api', methods=['POST'])
# def trajectory_api():
#     request_url = request.url
#     format = request.values['format']
#     if format == "MILIG":
#         form = MILIGUploadForm()
#         if form.validate_on_submit():
#             solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
#             return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))
#
#         return jsonify(data=form.errors)
#
#     elif format == "CAMS":
#         form = CAMSUploadForm()
#         if form.validate_on_submit():
#             solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
#             return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))
#
#         return jsonify(data=form.errors)
#
#     elif format == "RMSJSON":
#         form = RMSJSONUploadForm()
#         if form.validate_on_submit():
#             solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))
#             return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))
#
#         return jsonify(data=form.errors)
#
#     else:
#         return abort(400)


@app.route('/trajectory/temp/<uuid>/<filename>', methods=['GET'])
def load_temp_data(uuid, filename):
    file_path = os.path.join(app.config.get('TEMP_DIR'), uuid, filename)
    try:
        return send_file(file_path)
    except:
        return abort(404)
