from flask_wtf import FlaskForm
from wtforms import FileField, DecimalField, MultipleFileField, HiddenField
from wtforms.validators import InputRequired
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.widgets import html5


class UploadForm(FlaskForm):
    format = HiddenField("Format", validators=[InputRequired()])
    upload_methods = []

    # options
    max_toffset = DecimalField('max_toffset', places=2, default=5.00, widget=html5.NumberInput())
    v_init_part = DecimalField('v_init_part', places=2, default=0.25, widget=html5.NumberInput())
    v_init_ht = DecimalField('v_init_ht', places=2, default=-1, widget=html5.NumberInput())

    # TODO: recaptcha?
    # TODO: JSON option


class MILIGUploadForm(UploadForm):
    file_input = FileField("Single txt input file", validators=[FileRequired(), FileAllowed(['txt'], 'input file must be .txt file')])

    def __init__(self):
        UploadForm.__init__(self)
        self.format.process_data("MILIG")
        self.upload_methods = [self.file_input]


class CAMSUploadForm(UploadForm):
    file_FTP_detect_info = FileField("FTPdetectinfo", validators=[FileRequired(), FileAllowed(['txt'], 'input file must be .txt file')])
    file_camera_sites = FileField("CameraSites", validators=[FileRequired(), FileAllowed(['txt'], 'input file must be .txt file')])
    file_camera_time_offsets = FileField("CameraTimeOffsets", validators=[FileAllowed(['txt'], 'input file must be .txt file')])

    def __init__(self):
        UploadForm.__init__(self)
        self.format.process_data("CAMS")
        self.upload_methods = [self.file_FTP_detect_info, self.file_camera_sites, self.file_camera_time_offsets]


class RMSJSONUploadForm(UploadForm):
    files_json = MultipleFileField('Json files')

    def __init__(self):
        UploadForm.__init__(self)
        self.format.process_data("RMSJSON")
        self.upload_methods = [self.files_json]
