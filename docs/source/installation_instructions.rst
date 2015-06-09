How to install MXCuBE
-----------------
.. rubric:: Git repository
The MxCuBE Git repository can be found `here https://github.com/mxcube/mxcube`_

The repository includes two submodules, for both BlissFramework and HardwareRepository.
Cloning the repository:

.. code-block:: bash

   git clone https://github.com/mxcube/mxcube.git mxcube-2
   git checkout <latest_tag>
   git submodule init; git submodule update

Or alternatively you can clone the repository with the --recursive option.

Within the **bin** directory you can find scripts to start mxCuBE and the HWR server.
By default the *mxcube* script loads **mxcube.gui** ; this file is **not** shipped with 
the repository, for the first time it has to be created by making a copy of example_mxcube.gui.

.. code-block:: bash

   cp example_mxcube.gui mxcube.gui

.. rubric:: Dependencies

* Python >= 2.6
* PyQt 3.x
* PyQwt 5
* `louie (pydispatcher) <https://pypi.python.org/pypi/Louie/1.1>`_
* `gevent >= 1.0RC2 <https://github.com/downloads/surfly/gevent/gevent-1.0rc2.tar.gz>`_
* `Qub <http://github.com/mxcube/qub>`_
* `PyChooch <http://github.com/mxcube/pychooch>`_
* `PyMca <http://sourceforge.net/projects/pymca/>`_
* `PyTango <http://www.tango-controls.org/static/PyTango/latest/doc/html>`_

`SpecClient <http://github.com/mxcube/specclient>`_ is an optional dependency. If it is
not present, the Hardware Repository Server does not work, though. In this case
it is possible to specify a directory containing the Hardware Objects XML files instead
of a "host:port" string for the --hardwareRepository command line argument.

.. rubric:: Installing dependencies for Debian 6

The ESRF install of Debian 6 is pre-installed with PyQt and PyQwt 5.
Install PyTango and PyMca, make sure to be root.

.. code-block:: bash

   apt-get install pymca	
   apt-get install python2.6-pytango

Install the other dependenices needed through the blissinstaller or type the following as
blissadm:

.. code-block:: bash

   bliss_rpm Qub	
   bliss_rpm PyChooch
   bliss_rpm PyDispatcher
   bliss_rpm SpecClient-gevent
   bliss_rpm gevent

.. rubric::  Running mxCuBE

Once dependencies are satisfied, and the mxcube.gui is present, just run the mxcube
script:

    ./bin/mxcube --hardwareRepository=<directory or host:port>

See mxcube --help for more command line arguments.
