FROM ubuntu:22.04

# Build docker as (e.g.):
# docker build -t mxcube_qt5 ~/pycharm/mxcubeqt

# See start_mxcube for running and setting up docker

# Set terminal and time zone, to catch installer interaction attempts
ENV TERM linux
ENV TZ Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system packages
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y apt-utils curl git sudo wget \
    libldap2-dev libsasl2-dev libmemcached-dev ldap-utils tox lcov valgrind


# Get and update pip
RUN apt-get install python3-pip -y
RUN pip install --upgrade pip

# RUN pip install poetry
RUN pip install devtools

## mxcubeqt requirements
WORKDIR /tmp
COPY ./PyQt5_commercial-5.15.9-cp37-abi3-manylinux_2_17_x86_64.whl /tmp
RUN pip install ./PyQt5_commercial-5.15.9-cp37-abi3-manylinux_2_17_x86_64.whl
RUN apt-get install -y python3-pyqtgraph
RUN mkdir -p /tmp/mxcubecore
COPY ./requirements_mxcubecore.txt ./setup.py /tmp/mxcubecore/
WORKDIR /tmp/mxcubecore
RUN pip install .

# To link to $MXCUBE_ROOT, directory containing mxcuebqt and mxcubecore repositories
RUN mkdir -p /MXCuBE
WORKDIR /MXCuBE

#CMD ["python3",  "/MXCuBE/mxcubeqt/mxcubeqt/__main__.py", "--pyqt5", "--mockupMode",]
CMD ["python3",  "/MXCuBE/mxcubeqt/mxcubeqt/__main__.py", "--pyqt5"]
