import os, shutil, atexit
from trajectory import app as application

if __name__ == "__main__":

    def app_atexit():
        # remove all trajectory data
        temp_dir = application.config.get('TEMP_DIR')
        for file in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, file)):
                shutil.rmtree(os.path.join(temp_dir, file))
                print("removing", file)

    atexit.register(app_atexit)
    application.run(port=80, host='0.0.0.0', ssl_context='adhoc', threaded=True, debug=False)
