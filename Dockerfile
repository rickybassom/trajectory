FROM python:3.7

MAINTAINER Ricky Bassom

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    gcc gfortran python3-dev libffi-dev libssl-dev build-essential wget libfreetype6-dev libpng-dev libopenblas-dev libgeos-dev \
    python-qt4 python3-numpy python3-scipy python3-pandas cython python3-matplotlib python3-statsmodels python3-ephem libgl1-mesa-glx
# RUN apt-get install -y nginx uwsgi-core uwsgi-src uuid-dev uwsgi-plugin-python  # Un-comment for deployment

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python3.7/site-packages"

# ADD app/requirements.txt /app/requirements.txt
# ADD start.sh /app/start.sh
# ADD uwsgi.ini /app/uwsgi.ini 

# numpy needs to be installed before other packages
RUN pip install --upgrade pip --src /usr/local/src
RUN pip install --upgrade numpy --src /usr/local/src
RUN pip install --upgrade -r /app/requirements.txt --src /usr/local/src
RUN pip install --upgrade pyproj==1.9.6 --src /usr/local/src
RUN pip install --upgrade https://github.com/matplotlib/basemap/archive/master.zip --src /usr/local/src

# Cache
ADD app /app
COPY app /app

WORKDIR /app

EXPOSE 80

RUN cd WesternMeteorPyLib/ && python3 setup.py install

CMD ["python", "wsgi.py"]  # Comment for deployment

# Un-comment below for deployment
# COPY nginx.conf /etc/nginx 
# CMD ["./start.sh"]
