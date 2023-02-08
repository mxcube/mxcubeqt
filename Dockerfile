FROM ubuntu:22.04

# Build docker as:
# docker build --build-arg dockerhome=/home/rhfogh/dockerhome/ \
#  --build-arg data_root=/alt/rhfogh/calc/mxcube_data/ \
#  --build-arg gphl_software_root=/alt/rhfogh/Software/ \

# The environment variable MXCUBE_ROOT must be set to opint to the directory containing
# the mxcubeqt and mxcubecore repositories.

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

## The following ARGs must be directoried that exist on teh machjine runnig the docker
## Yo use for home directory of the docker
#ARG dockerhome=~/dockerhome
## To for root directory of raw and processed data directory trees
#ARG data_root=~/mxcube_qt_data
## Directory containing the GPhL/gphl_release directory
#ARG gphl_software_root=~/Software
#ENV DOCKER_HOME=$dockerhome
#ENV DATA_ROOT=$data_root
#ENV GPHL_SOFTWARE_ROOT=$gphl_software_root

## mxcubeqt requirements
WORKDIR /tmp
COPY ./PyQt5_commercial-5.15.9-cp37-abi3-manylinux_2_17_x86_64.whl /tmp
RUN pip install ./PyQt5_commercial-5.15.9-cp37-abi3-manylinux_2_17_x86_64.whl
RUN apt-get install -y python3-pyqtgraph
RUN mkdir -p /tmp/mxcubecore
COPY ./requirements_mxcubecore.txt ./setup.py /tmp/mxcubecore/
WORKDIR /tmp/mxcubecore
RUN pip install .

# Set up for running
# RUN mkdir -p $dockerhome
# RUN mkdir -p $data_root
# RUN mkdir -p $gphl_software_root

# To link to $MXCUBE_ROOT, directory containing mxcuebqt and mxcubecore repositories
RUN mkdir -p /MXCuBE
WORKDIR /MXCuBE

#CMD ["python3",  "/MXCuBE/mxcubeqt/mxcubeqt/__main__.py", "--pyqt5", "--mockupMode",]
CMD ["python3",  "/MXCuBE/mxcubeqt/mxcubeqt/__main__.py", "--pyqt5"]
