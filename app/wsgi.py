#!/usr/bin/python3
import os
import shutil, atexit

from trajectory import app

if __name__ == "__main__":

    def app_atexit():
        # remove all trajectory data
        temp_dir = app.config.get('TEMP_DIR')
        for file in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, file)):
                shutil.rmtree(os.path.join(temp_dir, file))
                print("removing", file)

    atexit.register(app_atexit)
    app.run(port=80, host='0.0.0.0', ssl_context='adhoc', threaded=True, debug=False)
