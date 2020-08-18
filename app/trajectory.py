import os, time, pickle, mpld3, json, numpy

from threading import Thread
from mpld3 import _display
import matplotlib.pyplot as plt

from wmpl.Utils.Pickling import loadPickle

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
    default_limits=["300 per day", "30 per hour"]
)

app.config['TEMP_DIR'] = os.path.join(app.root_path, 'static', 'temp_data')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

solver = WMPGTrajectoryFormSolver(app.config.get('TEMP_DIR'))

temp_lock = []
plt_clearing_lock = False


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

    return render_template('index.html', forms={"milig": milig_form, "cams": cams_form, "rmsjson": rmsjson_form})


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
                time.sleep(10 * 60)

                # wait until files are not been used
                uuid = solved_path[:request_url.rfind('/')]
                while uuid in temp_lock:
                    time.sleep(1)

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


@app.route('/trajectory/get-temp-file/<uuid>/<filename>', methods=['GET'])
def get_temp_file(uuid, filename):
    file_path = os.path.join(app.config.get('TEMP_DIR'), uuid, filename)

    if not is_safe_path(app.config.get('TEMP_DIR'), str(file_path)):
        return abort(404)
    try:
        return send_file(file_path, as_attachment=True)
    except:
        return abort(404)


@app.route('/trajectory/get-temp-plots/<uuid>', methods=['GET'])
def get_temp_plots(uuid):
    # enter files lock while
    temp_lock.append(uuid)

    file_path = os.path.join(app.config.get('TEMP_DIR'), uuid)

    if not is_safe_path(app.config.get('TEMP_DIR'), file_path):
        return abort(404)

    pickle_filename = "trajectory.pickle"
    try:
        traj = loadPickle(file_path, pickle_filename)
    except:
        return abort(404)

    # end lock
    temp_lock.remove(uuid)

    frag_pickle_dict = traj.savePlots(None, None, show_plots=False, ret_figs=True)
    frag_pickle_dict_json = {}
    for name, value in frag_pickle_dict.items():
        fig = pickle.loads(value)

        if len(fig.axes) == 2:
            fig.axes[1].patch.set_alpha(0.0)  # necessary for mpld3 to work with twinx()
            mpld3.plugins.clear(fig)  # disable zooming, moving ... due to double axis mpld3 problem

        if name == "orbit":
            plt.axis([-0.3, 0.3, -0.3, 0.3])  # zoom in
            fig.axes[0].view_init(elev=90, azim=90)  # top down view

        frag_pickle_dict_json[name] = mpld3.fig_to_dict(fig)

        # Refresh figure
        global plt_clearing_lock
        while plt_clearing_lock: pass
        plt_clearing_lock = True
        plt.clf()
        plt.close()
        plt_clearing_lock = False

    frag_pickle_dict_json_fixed = json.dumps(frag_pickle_dict_json, cls=NumpyEncoder)
    frag_pickle_dict_json_fixed = frag_pickle_dict_json_fixed.replace(', "visible": false',
                                                                      "")  # fixes https://github.com/mpld3/mpld3/issues/370
    frag_pickle_dict_json_fixed = frag_pickle_dict_json_fixed.replace(', "visible": true', "")
    return frag_pickle_dict_json_fixed


# https://security.openstack.org/guidelines/dg_using-file-paths.html
def is_safe_path(basedir, path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        return os.path.realpath(path).startswith(basedir)

    return os.path.abspath(path).startswith(basedir)


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
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


_display.NumpyEncoder = NumpyEncoder
