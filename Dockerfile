FROM python:3.7

MAINTAINER Ricky Bassom

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    gcc gfortran python3-dev libffi-dev libssl-dev build-essential wget libfreetype6-dev libpng-dev libopenblas-dev libgeos-dev \
    python-qt4 python3-numpy python3-scipy python3-pandas cython python3-matplotlib python3-statsmodels python3-ephem libgl1-mesa-glx

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python3.7/site-packages"

# Add to cache
ADD app/requirements.txt /app/requirements.txt

# numpy needs to be installed before other packages
RUN pip install --upgrade numpy
RUN pip install --upgrade -r /app/requirements.txt
RUN pip install --upgrade pyproj==1.9.6
RUN pip install --upgrade https://github.com/matplotlib/basemap/archive/master.zip

# Cache
ADD app /app
COPY app /app

WORKDIR /app

EXPOSE 80

#ENV PYTHONPATH "${PYTHONPATH}:/app/WesternMeteorPyLib/"

RUN cd WesternMeteorPyLib/ && python3 setup.py install

CMD ["python", "wsgi.py"]