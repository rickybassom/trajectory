from flask import Flask
from flask import render_template, send_from_directory


app = Flask(__name__, static_folder='')

@app.route('/trajectory/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/trajectory/')
def trajectory():
    # Milig.solveTrajectoryMILIG()

    return render_template('index.html')

@app.route('/trajectory/test')
def hello():
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
