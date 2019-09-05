# trajectory
[![Build Status](https://travis-ci.com/rickybas/trajectory.svg?token=1Qmp7ACzet4TDsEVzALn&branch=master)](https://travis-ci.com/rickybas/trajectory)

https://globalmeteornetwork.org/trajectory/

Using [WesternMeteorPyLib](https://github.com/wmpg/WesternMeteorPyLib)

## Building and running

`git submodule update --init --recursive`

`docker build -t trajectory .`

`docker run -p 80:80 trajectory`

Open https://0.0.0.0:80/trajectory/

or when developing:

``docker run -p 80:80 -v `pwd`/app:/app trajectory``