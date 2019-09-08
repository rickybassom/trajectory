import time, json, uuid, os, zipfile, shutil
from io import BytesIO

from werkzeug.utils import secure_filename
from wtforms import FileField, MultipleFileField

from wmpl.Formats.Milig import solveTrajectoryMILIG
from wmpl.Formats.CAMS import solveTrajectoryCAMS, loadCameraSites, loadCameraTimeOffsets, loadFTPDetectInfo
from wmpl.Formats.RMSJSON import solveTrajectoryRMS


class WMPGTrajectoryFormSolver:

    def __init__(self, temp_dir):
        self.temp_dir = temp_dir

    def solve_for_json(self, form, format, url_base):
        """
        Return JSON of output directory including zip

        :param form:
        :return:
        """

        try:
            uuid_path = self._solve(form, format)
        except Exception as e:
            raise e

        json_files = []
        for file in os.listdir(uuid_path):
            json_files.append(url_base + os.path.join("/temp", os.path.basename(uuid_path), file))

        zip_file = self._create_zip(uuid_path)
        json_files.append(url_base + os.path.join("/temp", os.path.basename(uuid_path), zip_file))

        return json_files

    def _create_zip(self, output_dir):
        """
        Return filename of zip of output_dir

        :param form:
        :param format:
        :return:
        """

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = "output_{}.zip".format(timestr)

        # create zip in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            lenDirPath = len(output_dir)
            for root, _, files in os.walk(output_dir):
                for file in files:
                    filePath = os.path.join(root, file)
                    zipf.write(filePath, filePath[lenDirPath:])
        memory_file.seek(0)

        # save zip
        with open(os.path.join(output_dir, filename), 'wb') as f:
            shutil.copyfileobj(memory_file, f, length=131072)

        return filename

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
            filenames = self.save_files_from_form(form.upload_methods, dir_path)
            try:
                solveTrajectoryMILIG(dir_path, filenames['file_input'], max_toffset=max_toffset,
                                     v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False, show_plots=False, verbose=False)
            except:
                raise Exception("Input files incorrect")

        elif format == "CAMS":
            filenames = self.save_files_from_form(form.upload_methods, dir_path)

            try:
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
                                    v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False, show_plots=False, verbose=False)
            except:
                raise Exception("Input files incorrect")

        elif format == "RMSJSON":
            filenames = self.save_files_from_form(form.upload_methods, dir_path)

            # Load all json files
            json_list = []
            for json_file in filenames.values():
                with open(os.path.join(dir_path, json_file)) as f:
                    data = json.load(f)
                    json_list.append(data)

            try:
                solveTrajectoryRMS(json_list, max_toffset=max_toffset,
                               v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False, show_plots=False, verbose=False)
            except:
                raise Exception("Input files incorrect")
        else:
            assert "Format not found"

        return dir_path

    def save_files_from_form(self, upload_methods, dir_path):
        """
        Returns saved filenames of files entered in the form

        :param files_data:
        :param extensions:
        :param dir_path:
        :return:
        """

        saved_file_names = dict()  # type of file (e.g FTPdetectinfo) : filename
        for upload_method in upload_methods:
            if not upload_method.data and not upload_method.flags.required:
                continue
            elif not upload_method.data:
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
                saved_file_names[upload_method.label.field_id] = filename
                upload_method.data.save(os.path.join(dir_path, filename))

            else:
                assert "Upload method" + str(type(upload_method)) + "not available"

        return saved_file_names
