import os

from flask import Flask
from flask import render_template, abort, send_file
from flask_bootstrap import Bootstrap
from flask_restful import Api

from upload_forms import MILIGUploadForm, CAMSUploadForm, RMSJSONUploadForm

from restful_upload_form import RestfulUploadForm

app = Flask(__name__)
api = Api(app)
Bootstrap(app)

app.config['TEMP_DIR'] = os.path.join(app.root_path, 'static', 'temp_data')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

api.add_resource(RestfulUploadForm, '/trajectory/api')


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

    return render_template('index.html', milig_form=milig_form, cams_form=cams_form, rmsjson_form=rmsjson_form)


@app.route('/trajectory/temp/<uuid>/<filename>', methods=['GET'])
def load_temp_data(uuid, filename):
    file_path = os.path.join(app.config.get('TEMP_DIR'), uuid, filename)
    try:
        return send_file(file_path)
    except:
        return abort(404)
