PYTHON=python3.7 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python37"
mv python37_plugin.so /usr/lib/uwsgi/plugins/python37_plugin.so
chmod 644 /usr/lib/uwsgi/plugins/python37_plugin.so
