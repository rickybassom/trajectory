from flask import request, jsonify
from flask_restful import  Resource, abort
from wmpg_trajectory_form_solver import WMPGTrajectoryFormSolver

from upload_forms import MILIGUploadForm, CAMSUploadForm, RMSJSONUploadForm

import trajectory


class RestfulUploadForm(Resource):
    def post(self):
        request_url = request.url
        format = request.values['format']
        if format == "MILIG":
            form = MILIGUploadForm()
            if form.validate_on_submit():
                solver = WMPGTrajectoryFormSolver(trajectory.app.config.get('TEMP_DIR'))
                return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))

            return jsonify(data=form.errors)

        elif format == "CAMS":
            form = CAMSUploadForm()
            if form.validate_on_submit():
                solver = WMPGTrajectoryFormSolver(trajectory.app.config.get('TEMP_DIR'))
                return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))

            return jsonify(data=form.errors)

        elif format == "RMSJSON":
            form = RMSJSONUploadForm()
            if form.validate_on_submit():
                solver = WMPGTrajectoryFormSolver(trajectory.app.config.get('TEMP_DIR'))
                return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))

            return jsonify(data=form.errors)

        else:
            return abort(400)