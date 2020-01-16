import mpld3, json, numpy

# FIX: https://github.com/mpld3/mpld3/issues/434
class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(obj, (numpy.int_, numpy.intc, numpy.intp, numpy.int8,
                            numpy.int16, numpy.int32, numpy.int64, numpy.uint8,
                            numpy.uint16, numpy.uint32, numpy.uint64)):
            return int(obj)
        elif isinstance(obj, (numpy.float_, numpy.float16, numpy.float32,
                              numpy.float64)):
            return float(obj)
        elif isinstance(obj, (numpy.ndarray,)):  #### This is the fix
            print("here")
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

from mpld3 import _display
_display.NumpyEncoder = NumpyEncoder

import os, time
import pickle
from threading import Thread

from flask import Flask, request, jsonify
from flask import render_template, abort, send_file
from flask_bootstrap import Bootstrap
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from upload_forms import MILIGUploadForm, CAMSUploadForm, RMSJSONUploadForm
from wmpg_trajectory_form_solver import WMPGTrajectoryFormSolver

from wmpl.Utils.Pickling import loadPickle

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

solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))

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
            solved_path, solved_data = solver.solve_for_json(form, format, request_url[:request_url.rfind('/')])

            def remove_trajectory_files(solved_path):
                time.sleep(60 * 10)
                solver.remove_saved_files(solved_path)

            thread = Thread(target=remove_trajectory_files, kwargs={'solved_path': solved_path})
            thread.start()

            return jsonify(solved_data)
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

    if not is_safe_path(app.config.get('TEMP_DIR'), str(file_path)):
        return abort(404)

    try:
        return send_file(file_path, as_attachment=True)
    except:
        return abort(404)

@app.route('/trajectory/temp-get-plots/<uuid>', methods=['GET'])
def get_temp_plots(uuid):
    file_path = os.path.join(app.config.get('TEMP_DIR'), uuid)

    if not is_safe_path(app.config.get('TEMP_DIR'), file_path):
        return abort(404)

    pickle_filename = [f for f in os.listdir(file_path) if f.endswith('.pickle')][0]
    traj = loadPickle(file_path, pickle_filename)

    frag_pickle_dict = traj.savePlots(None, None, show_plots=False, ret_figs=True)
    frag_pickle_dict_json = {}
    for key, value in frag_pickle_dict.items():
        print(key)
        fig = pickle.loads(value)
        frag_pickle_dict_json[key] = mpld3.fig_to_dict(fig)

    return json.dumps(frag_pickle_dict_json, cls=NumpyEncoder)

# https://security.openstack.org/guidelines/dg_using-file-paths.html
def is_safe_path(basedir, path, follow_symlinks=True):
  # resolves symbolic links
  if follow_symlinks:
    return os.path.realpath(path).startswith(basedir)

  return os.path.abspath(path).startswith(basedir)

