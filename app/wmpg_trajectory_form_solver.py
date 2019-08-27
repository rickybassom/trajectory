import time
import uuid, os, zipfile, json
from io import BytesIO

from flask import send_file
from werkzeug.utils import secure_filename
from wtforms import FileField, MultipleFileField

from wmpl.Formats.Milig import solveTrajectoryMILIG
from wmpl.Formats.CAMS import solveTrajectoryCAMS, loadCameraSites, loadCameraTimeOffsets, loadFTPDetectInfo
from wmpl.Formats.RMSJSON import solveTrajectoryRMS


class WMPGTrajectoryFormSolver:

    def __init__(self, temp_dir):
        self.temp_dir = temp_dir

    def solveForZip(self, form, format):
        """
        Return zip of output

        :param form:
        :param format:
        :return:
        """
        output_dir = self._solve(form, format)

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = "output_{}.zip".format(timestr)

        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            lenDirPath = len(output_dir)
            for root, _, files in os.walk(output_dir):
                for file in files:
                    filePath = os.path.join(root, file)
                    zipf.write(filePath, filePath[lenDirPath:])
        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename=filename
        )

    def solveForJSON(self, form):
        """
        Return JSON of

        :param form:
        :return:
        """
        return self._solve(form, format)

    def _solve(self, form, format):
        """
        Run wmpg trajectory solver and return the directory path of the output files

        :param form:
        :return:
        """
        dir_path = os.path.join(self.temp_dir, uuid.uuid4().hex)
        max_toffset = float(form.max_toffset.data)
        v_init_part = float(form.v_init_part.data)
        v_init_ht = float(form.v_init_ht.data) if form.v_init_ht.data != -1 else None

        os.mkdir(dir_path)

        if format == "MILIG":
            filenames = self.saved_files_from_form(form.upload_methods, dir_path)
            solveTrajectoryMILIG(dir_path, filenames['file_input'], max_toffset=max_toffset,
                                 v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False)

        elif format == "CAMS":
            filenames = self.saved_files_from_form(form.upload_methods, dir_path)

            # Get locations of stations
            stations = loadCameraSites(os.path.join(dir_path, filenames["file_camera_sites"]))

            time_offsets = None
            if 'file_camera_time_offsets' in filenames:
                # Get time offsets of cameras
                time_offsets = loadCameraTimeOffsets(os.path.join(dir_path, filenames["file_camera_time_offsets"]))

            # Get the meteor data
            meteor_list = loadFTPDetectInfo(os.path.join(dir_path, filenames["file_FTP_detect_info"]), stations,
                                            time_offsets=time_offsets)

            solveTrajectoryCAMS(meteor_list, dir_path, max_toffset=max_toffset,
                                v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False)
        elif format == "RMSJSON":
            filenames = self.saved_files_from_form(form.upload_methods, dir_path)

            # Load all json files
            json_list = []
            for json_file in filenames.values():
                with open(os.path.join(dir_path, json_file)) as f:
                    data = json.load(f)
                    json_list.append(data)

            solveTrajectoryRMS(json_list, max_toffset=max_toffset,
                               v_init_part=v_init_part, v_init_ht=v_init_ht)
        else:
            assert "Format not found"

        return dir_path

    def saved_files_from_form(self, upload_methods, dir_path):
        """
        Returns saved filenames

        :param files_data:
        :param extensions:
        :param dir_path:
        :return:
        """

        saved_file_names = dict() # type of file (e.g FTPdetectinfo) : filename
        for upload_method in upload_methods:
            def validator_used_in_field(field, validator_type):
                for validator in field.validators:
                    if type(validator) is validator_type:
                        return True

                return False

            # if
            if not upload_method.data and not upload_method.flags.required:
                continue
            else:
                assert "No files uploaded in required field"

            if type(upload_method) is MultipleFileField:
                count = 0
                for file in upload_method.data:
                    filename = secure_filename(file.filename)
                    saved_file_names[upload_method.label.field_id + str(count)] = filename
                    file.save(os.path.join(dir_path, filename))
                    count += 1

            elif type(upload_method) is FileField:
                filename = secure_filename(upload_method.data.filename)
                print()
                saved_file_names[upload_method.label.field_id] = filename
                upload_method.data.save(os.path.join(dir_path, filename))

            else:
                assert "Upload method" + str(type(upload_method)) + "not available"

        return saved_file_names
