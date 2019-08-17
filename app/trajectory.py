import os

from flask import Flask
from flask import render_template, send_from_directory
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import RadioField, MultipleFileField, DecimalField
from wtforms.validators import InputRequired
from wtforms.widgets import html5

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
        return "the form has been submitted " + form.format.data

    return render_template('index.html', form=form)


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


class UploadForm(FlaskForm):
    format = RadioField('Supported formats:', choices=[('MILIG', 'MILIG'), ('CAMS', 'CAMS'), ('JSON', 'JSON')],
                        default='MILIG', validators=[InputRequired()])
    files = MultipleFileField('File(s) upload', validators=[InputRequired()])

    # options
    max_toffset = DecimalField('max_toffset', places=2, default=5.00, widget=html5.NumberInput())
    v_init_part = DecimalField('v_init_part', places=2, default=0.25, widget=html5.NumberInput())
    v_init_ht = DecimalField('v_init_ht', places=2, default=None)

    # TODO: recaptcha???
