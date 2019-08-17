import os

from flask import Flask
from flask import render_template, send_from_directory
from flask_bootstrap import Bootstrap

from upload_form import UploadForm
from wmpg_trajectory_solver import WMPGTrajectorySolver

app = Flask(__name__, static_folder='/trajectory/')
Bootstrap(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/trajectory/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/trajectory/', methods=['GET', 'POST'])
def trajectory():
    form = UploadForm()

    if form.validate_on_submit():
        solver = WMPGTrajectorySolver()
        return solver.solve(form)

    return render_template('index.html', form=form)


@app.route('/trajectory/test')
def test():
    import datetime
    import math

    # Import modules from WMPL
    import wmpl.Utils.TrajConversions as trajconv
    import wmpl.Utils.SolarLongitude as sollon

    # Compute the Julian date of the current time
    jd_now = trajconv.datetime2JD(datetime.datetime.now())

    # Get the solar longitude of the current time (in radians)
    lasun = sollon.jd2SolLonJPL(jd_now)

    return str(math.degrees(lasun)), ' deg'
