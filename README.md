# trajectory
[![Build Status](https://travis-ci.com/rickybas/trajectory.svg?token=1Qmp7ACzet4TDsEVzALn&branch=master)](https://travis-ci.com/rickybas/trajectory)

https://globalmeteornetwork.org/trajectory/

`git submodule update --init --recursive`

` sudo docker build -t trajectory .`

`sudo docker run -p 80:80 trajectory`

Open https://0.0.0.0:80/trajectory/

or when developing:

`` sudo docker run -p 80:80 -v `pwd`/app:/app trajectory``