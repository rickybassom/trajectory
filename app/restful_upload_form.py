from flask import request, jsonify
from flask_restful import Resource, abort

from wmpg_trajectory_form_solver import WMPGTrajectoryFormSolver

import trajectory

class RestfulUploadForm(Resource):
    def post(self):
        request_url = request.url
        format = request.values['format']

        forms = trajectory.app.config.get('FORMS')
        form = forms[format]()

        if form.validate_on_submit():
            try:
                solver = WMPGTrajectoryFormSolver(trajectory.app.config.get('TEMP_DIR'))
            except Exception as e:
                print(e)
                abort(400)
            else:
                if form.output_type.data == "json":
                    return jsonify(solver.solve_for_json(form, format, request_url[:request_url.rfind('/')]))
                else: # form.output_type.data == "zip"
                    return solver.solve_for_zip(form, format)

        return jsonify(data=form.errors), 400
