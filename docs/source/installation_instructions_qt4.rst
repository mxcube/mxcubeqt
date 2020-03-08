How to install and run Qt version
#################################

In this page a sequence how to get software code, install dependencies and execute software is described.

Tested with:

* Linux: Ubuntu 10, 12, 14, 16 (with gnome and kde) and Centos 7 (with gnome)
* MacOs.

*****************
1. Git repository
*****************

The MXCuBE source code can be found `here <https://github.com/mxcube/mxcube>`_
To get MXCuBE code execute:

.. code-block:: bash

   git clone https://github.com/mxcube/mxcube.git mxcube-2
   cd mxcube-2
   git submodule init
   git submodule update

**********************
2. Python dependencies
**********************

MXCuBE supports Qt4, Qt5 and PySide. Start script automaticaly detects and imports available version of Qt.

* `Qt4 <http://doc.qt.io/qt-4.8/>`_
* `Qt5 <http://doc.qt.io/qt-5/>`_
* `PySide <https://wiki.qt.io/PySide>`_

Other dependencies:

* `Python (>2.6) <https://www.python.org/>`_
* `louie (pydispatcher) <https://pypi.python.org/pypi/Louie/1.1>`_
* `gevent >= 1.0RC2 <https://github.com/downloads/surfly/gevent/gevent-1.0rc2.tar.gz>`_
* `suds <https://pypi.python.org/pypi/suds>`_
* `jsonpickle <https://pypi.python.org/pypi/jsonpickle/0.7.0>`_
* `yaml <https://pypi.python.org/pypi/PyYAML/3.12>`_
* `scipy stack <http://www.scipy.org/install.html>`_
* `enum34 <https://pypi.org/project/enum34/>`_
* `PyChooch <http://github.com/mxcube/pychooch>`_
* `PyMca <http://sourceforge.net/projects/pymca/>`_
* `OpenCV <https://pypi.org/project/opencv-python/>`_

2.1. Debian/Ubuntu
==================

Python 2x

.. code-block:: bash

   sudo apt-get install python-qt4 python-gevent python-louie python-jsonpickle python-yaml python-numpy python-scipy python-matplotlib python-suds pymca
   sudo pip install enum34

If Qt5 used:

.. code-block:: bash

   sudo apt-get install PyMca5
   
Python 3x

.. code-block:: bash

   sudo pip3 install PyQt5 gevent numpy scipy matplotlib jsonpickle PyMca5 opencv-python enum34 Louie suds3 PyYAML PyMca5

2.2. Fedora/Centos
==================

.. code-block:: bash

   sudo yum install qt qt-demos qt-designer qt4 qt4-designer PyQt4 PyQt4-webkit numpy scipy python-pip
   sudo pip install matplotlib PyDispatcher enum34

Some hints if problems during ``sudo pip install matplotlib``:

.. code-block:: bash

   # missing libpng
   sudo yum install libpng-devel
   # gcc error
   sudo yum install gcc-c++

2.3. Installing dependencies with pip
=====================================

.. code-block:: bash
   sudo pip install PyQt

2.4. PyMca
==========

If pymca is not available via package management tool then:

.. code-block:: bash

   # download source from: http://pymca.sourceforge.net/download.html
   sudo python setup.py install

   # when Qwt not available
   # download source from http://sourceforge.net/projects/qwt/files/qwt/
   qt4-qmake qwt.pro
   sudo make install

More info:

* http://pymca.sourceforge.net/
* http://qwt.sourceforge.net/index.html

2.5. OpenSUSE clean install
===========================

This describes installing dependencies for Qt4 on a clean OpenSUSE Leap 42 system.
It has the  advantage of giving precise versions for dependencies.

I use the Miniconda (python 2.7) version of the Anaconda environment manager,
starting in a completely empty enviroment, here named 'mxpath'

Installation is complicated because both conda and pip default to the newest
version of each installed dependency. We are limited to numpy < 1.9
(to preserve the oldnumeric link) and Qt4, neither of which is the newest
package, and the various cross-dependencies makes it tricky to find a
consistent set. The two first installs must be done in that order and with
those switches for this reason:

.. code-block:: bash

   conda create -n mxpath
   source activate mxpath
   conda install -n mxpath matplotlib=1.3
   conda install -n mxpath scipy --no-update-deps
   conda install -n mxpath pydispatcher
   conda install -n mxpath gevent
   conda install -n mxpath pyyaml
   pip install  jsonpickle
   pip install  Louie

Installing PyMca:

pip install gives only version 5.1.3, whereas we need version 4.

To install PyMca version 4, you must:

  - Make sure you have gcc, python-devel, Mesa-libGL-devel, glu-devel,
    numpy-devel and libqwt5 installed on your system.

  - Download pymca4.7.4-src.tgz from
    https://sourceforge.net/projects/pymca/files/pymca/
    and cd into the unzipped directory.

  - python setup.py install --install-lib /path-to-miniconda/envs/mxpath/lib/python2.7/site-packages

***************
3. Running code
***************

Use **mxcube** script file located in **bin** directory with
command line arguments to launch MXCuBE.

.. code-block:: bash

   Usage: mxcube <GUI definition file> [options]

   Options:
	  -h, --help            show this help message and exit
	  --logFile=FILE        Log file
	  --logLevel=LOGLEVEL   Log level
	  --bricksDirs=dir1:dir2...dirN
	               Additional directories for bricks search path (you can
                       also use the CUSTOM_BRICKS_PATH environment variable)
	  --hardwareRepository=dir
                               Directory where configuration xml files are located
	  --hardwareObjectsDirs=dir1:dir2...dirN
        	                Additional directories for Hardware Objects search
                	        path (you can also use the
                        	CUSTOM_HARDWARE_OBJECTS_PATH environment variable)
	  -d                    start GUI in Design mode
	  -m                    maximize main window
	  --no-border           does not show borders on main window

**run_mxcube.csh*** script file located in **bin** directory can be adjusted and used.
For example to run MXCuBE with default parameters edit script:

.. code-block:: bash

   PATH_TO_MXCUBE/bin/mxcube --hardwareRepository=PATH_TO_MXCUBE/ExampleFiles/HardwareObjects.xml

It is possible to adjust script by defining gui configuration file, additional directories for bricks and hardware objects. For example:

.. code-block:: bash

   PATH_TO_MXCUBE/bin/mxcube PATH_TO_GUI_FILE --hardwareRepository=PATH_TO_XML_FILES  --hardwareObjectsDirs=PATHs_TO_ADDITIONAL_HARDWARE_OBJECTS --bricksDirs=PATHS_TO_ADDITIONAL_BRICKS

Example xml files are available `here <https://github.com/mxcube/mxcube/tree/master/ExampleFiles/HardwareObjects.xml>`_

3.1. GUI builder
================

GUI builder is used to define GUI layout. It is possible to add, edit or remove bricks,
change brick parameters, edit signals and slots between bricks.
To launch gui builder add **-d**. For example:

.. code-block:: bash

   PATH_TO_MXCUBE/bin/mxcube --hardwareRepository=PATH_TO_MXCUBE/ExampleFiles/HardwareObjects.xml -d

*****************
Other information
*****************

* :doc:`how_to_create_hwobj`
* :doc:`how_to_create_qt_brick`
* :doc:`how_to_define_qt_gui`
