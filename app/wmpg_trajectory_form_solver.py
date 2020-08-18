import time, uuid, os, zipfile, shutil, json
from io import BytesIO

from werkzeug.utils import secure_filename
from wtforms import FileField, MultipleFileField

from wmpl.Formats.Milig import solveTrajectoryMILIG
from wmpl.Formats.CAMS import solveTrajectoryCAMS, loadCameraSites, loadCameraTimeOffsets, loadFTPDetectInfo
from wmpl.Formats.RMSJSON import solveTrajectoryRMS

from wmpl.Utils.Pickling import savePickle


class WMPGTrajectoryFormSolver:

    def __init__(self, temp_dir):
        self.temp_dir = temp_dir

    def solve_for_json(self, form, format, url_base):
        """
        Return JSON of output directory including zip

        :param form: (UploadForm) the form object submitted by the user
        :param format: (str) supported input data format (MILIG, CAMS and RMSJSON currently)
        :param url_base: (str) url base e.g. 0.0.0.0:80
        :raises Exception: if form received cannot be solved
        :return: (tuple) solved data full path, json of the data id and files urls
        """

        try:
            uuid_path = self._solve(form, format)
        except Exception as e:
            raise e

        uuid = os.path.basename(uuid_path)

        json_files = []
        for file in os.listdir(uuid_path):
            json_files.append(url_base + os.path.join("/get-temp-file", uuid, file))

        zip_file = self._create_zip(uuid_path)
        json_files.append(url_base + os.path.join("/get-temp-file", uuid, zip_file))

        data = {}
        data["id"] = uuid
        data["files"] = json_files

        return uuid_path, data

    def _create_zip(self, output_dir):
        """
        Return filename of output_dir zip

        :param output_dir: (string) desired location of zip
        :return: (str) filename of created zip
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

        :param form: (UploadForm) the form object submitted by the user
        :param format: (str) supported input data format (MILIG, CAMS and RMSJSON currently)
        :return: (str) directory of output
        """

        dir_path = os.path.join(self.temp_dir, uuid.uuid4().hex)
        max_toffset = float(form.max_toffset.data)
        v_init_part = float(form.v_init_part.data)
        v_init_ht = float(form.v_init_ht.data) if form.v_init_ht.data != -1 else None

        os.mkdir(dir_path)

        if format == "MILIG":
            filenames = self._save_files_from_form(form.upload_methods, dir_path)
            try:
                traj = solveTrajectoryMILIG(dir_path, filenames['file_input'], max_toffset=max_toffset,
                                            v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False,
                                            save_results=False, show_plots=False, verbose=False)
                traj.saveReport(dir_path, "report.txt")
                savePickle(traj, dir_path, "trajectory.pickle")
            except:
                self.remove_saved_files(dir_path)
                raise Exception("Input files incorrect")

        elif format == "CAMS":
            filenames = self._save_files_from_form(form.upload_methods, dir_path)

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

                traj = solveTrajectoryCAMS(meteor_list, dir_path, max_toffset=max_toffset,
                                           v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False,
                                           save_results=False, show_plots=False, verbose=False)
                traj.saveReport(dir_path, "report.txt")
                savePickle(traj, dir_path, "trajectory.pickle")
            except:
                self.remove_saved_files(dir_path)
                raise Exception("Input files incorrect")

        elif format == "RMSJSON":
            filenames = self._save_files_from_form(form.upload_methods, dir_path)

            # Load all json files
            json_list = []
            for json_file in filenames.values():
                with open(os.path.join(dir_path, json_file)) as f:
                    data = json.load(f)
                    json_list.append(data)

            try:
                traj = solveTrajectoryRMS(json_list, dir_path, max_toffset=max_toffset,
                                          v_init_part=v_init_part, v_init_ht=v_init_ht, monte_carlo=False,
                                          show_plots=False, save_results=False, verbose=False)
                traj.saveReport(dir_path, "report.txt")
                savePickle(traj, dir_path, "trajectory.pickle")
            except:
                self.remove_saved_files(dir_path)
                raise Exception("Input files incorrect")
        else:
            assert "Format not found"

        return dir_path

    def _save_files_from_form(self, upload_methods, dir_path):
        """
        Returns saved filenames of files entered in the form

        :param upload_methods: ([UploadForm]) currently available forms of inputting data
        :param dir_path: (str) path to save files
        :return: (dict) saved file names
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
                    if file.filename.endswith(".txt") or file.filename.endswith(".json"):
                        filename = secure_filename(file.filename)
                        saved_file_names[upload_method.label.field_id + str(count)] = filename
                        file.save(os.path.join(dir_path, filename))
                        count += 1
                    else:
                        assert "File added with illegal extension"

            elif type(upload_method) is FileField:
                if upload_method.data.filename.endswith(".txt") or upload_method.data.filename.endswith(".json"):
                    filename = secure_filename(upload_method.data.filename)
                    saved_file_names[upload_method.label.field_id] = filename
                    upload_method.data.save(os.path.join(dir_path, filename))
                else:
                    assert "File added with illegal extension"

            else:
                assert "Upload method" + str(type(upload_method)) + "not available"

        return saved_file_names

    def remove_saved_files(self, uuid_directory):
        """
        Removes directory of outputted trajectory data

        :param uuid_directory: (str) directory of outputted files to remove
        """
        print("removing", uuid_directory)
        shutil.rmtree(uuid_directory)
