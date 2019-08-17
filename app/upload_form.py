from flask_wtf import FlaskForm
from wtforms import RadioField, MultipleFileField, DecimalField
from wtforms.validators import InputRequired
from wtforms.widgets import html5

class UploadForm(FlaskForm):
    format = RadioField('Supported formats:', choices=[('MILIG', 'MILIG'), ('CAMS', 'CAMS'), ('JSON', 'JSON')],
                        default='MILIG', validators=[InputRequired()])
    files = MultipleFileField('File(s) upload', validators=[InputRequired()])

    # options
    max_toffset = DecimalField('max_toffset', places=2, default=5.00, widget=html5.NumberInput())
    v_init_part = DecimalField('v_init_part', places=2, default=0.25, widget=html5.NumberInput())
    v_init_ht = DecimalField('v_init_ht', places=2, default=None)

    # TODO: recaptcha?