# mxCuBE

mxCuBE stands for macromolecular xtallography customized beamline environment;
the project started in 2005 at [ESRF](http://www.esrf.eu), since then it has
been adopted by other institutes in Europe. In 2010, a collaboration
agreement has been signed for the development of mxCuBE with the following
partners:
* ESRF
* [Soleil](http://www.synchrotron-soleil.fr/)
* [Max lab](https://www.maxlab.lu.se/)
* [HZB](http://www.helmholtz-berlin.de/)
* [EMBL](http://www.embl.org/)
* [Global Phasing Ltd.](http://www.globalphasing.com/)

mxCuBE consists of 2 main parts:
* a graphical user interface
* data acquisition control layer

## Graphical user interface

mxCuBE GUI is built on top of the [Bliss Framework](http://github.com/mxcube/BlissFramework),
a tool developed at ESRF for building graphical interfaces based on Python 2.x
and the Qt 3 toolkit, especially designed for beamline experiment control applications.

## Data acquisition control

Data acquisition control is made of Hardware Objects. Hardware Objects are Python
classes associated with a configuration XML file. Hardware Objects are instanciated
by the [Hardare Repository](http://github.com/mxcube/HardwareRepository).

Each Hardware Object should be based on an abstract class, defining a common API
for mxCuBE. Then, implementation differs at each site depending on hardware and
beamline specificities.

## Installing mxCuBE

### git repository organization

This repository includes two submodules, for both BlissFramework and HardwareRepository.
Cloning can be done by the following commands:

    git clone https://github.com/mxcube/mxcube.git mxcube-2
    git checkout <latest_tag>
    git submodule init; git submodule update

Within the *bin* directory you can find scripts to start mxCuBE and the HWR server.
By default the *mxcube* script loads *mxcube.gui* ; this file is **not** shipped with 
the repository, for the first time it has to be created by making a copy of example_mxcube.gui.

     cp example_mxcube.gui mxcube.gui

### Dependencies

* Python >= 2.6
* PyQt 3.x
* PyQwt 5
* [louie (pydispatcher)](https://pypi.python.org/pypi/Louie/1.1)
* [gevent >= 1.0RC2](https://github.com/downloads/surfly/gevent/gevent-1.0rc2.tar.gz)
* [Qub](http://github.com/mxcube/qub)
* [PyChooch](http://github.com/mxcube/pychooch)
* [PyMca](http://sourceforge.net/projects/pymca/)
* [jsonpickle](https://pypi.python.org/pypi/jsonpickle/0.7.0)

[PyTango](http://www.tango-controls.org/static/PyTango/latest/doc/html/) and
[SpecClient](http://github.com/mxcube/specclient) are optional dependencies.

If SpecClient is not present, the Hardware Repository Server does not work, though.
In this case just specify a directory containing the Hardware Objects XML
files instead of a "host:port" string for the --hardwareRepository command line argument.

## Running mxCuBE

Once dependencies are satisfied, and the mxcube.gui is present, just run the mxcube
script:

    ./bin/mxcube --hardwareRepository=<directory or host:port>

See mxcube --help for more command line arguments.
