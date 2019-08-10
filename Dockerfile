FROM python:3.7-alpine

MAINTAINER Ricky Bassom

RUN apk --update --no-cache --update-cache \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        add gcc gfortran python3-dev libffi-dev openssl-dev build-base wget freetype-dev libpng-dev openblas-dev py3-qt5 geos-dev geos \
            py3-scipy py3-pandas cython py3-matplotlib

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

ENV PYTHONPATH "${PYTHONPATH}:/usr/lib/python3.7/site-packages

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