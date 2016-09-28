How to install and run Qt version
#################################

MXCuBE is organized as a subset of several git submodules. 
In this page a sequence how to get software code, install dependencies and execute software is described.

Tested with:

* Linux: Ubuntu 10, 12, 14 (with gnome and kde) and Centos 7 (with gnome)
* Macos.

*****************
1. Git repository
*****************

The MXCuBE is hosten in several git projects that all together can be found `here <https://github.com/mxcube/mxcube>`_
The repository for Qt version is organized in three submodules:

* `HardwareRepository <https://github.com/mxcube/HardwareRepository.git>`_
* `HardwareObjects <https://github.com/mxcube/HardwareObjects.git>`_
* `BlissFramework <https://github.com/mxcube/BlissFramework.git>`_

To get MXCuBE code execute:

.. code-block:: bash

   git clone https://github.com/mxcube/mxcube.git mxcube-2
   cd mxcube-2
   git submodule init
   git submodule update

**********************
2. Python dependencies
**********************

* `Python (>2.6) <https://www.python.org/>`_
* `Qt4 <http://doc.qt.io/qt-4.8/)>`_
* `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_ 
* `louie (pydispatcher) <https://pypi.python.org/pypi/Louie/1.1>`_
* `gevent >= 1.0RC2 <https://github.com/downloads/surfly/gevent/gevent-1.0rc2.tar.gz>`_
* `PyChooch <http://github.com/mxcube/pychooch>`_
* `PyMca <http://sourceforge.net/projects/pymca/>`_
* `jsonpickle <https://pypi.python.org/pypi/jsonpickle/0.7.0>`_
* `scipy stack <http://www.scipy.org/install.html>`_

Before installing dependencies it is recomended to run mxcube (see :) to see
which dependencies are missing.

2.1. Debian/Ubuntu
==================

.. code-block:: bash

   sudo apt-get install python-qt4 python-gevent python-louie python-jsonpickle python-numpy python-scipy python-matplotlib python-suds pymca 

2.2. Fedora/Centos
==================

.. code-block:: bash

   sudo yum install qt qt-demos qt-designer qt4 qt4-designer PyQt4 PyQt4-webkit numpy scipy python-pip
   sudo pip install matplotlib PyDispatcher

Some hints if problems during ``sudo pip install matplotlib``:

.. code-block:: bash

   # missing libpng
   sudo yum install libpng-devel
   # gcc error 
   sudo yum install gcc-c++
  
2.3. PyMca
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
    

***************
3. Running code
***************

Use **mxcube** script file located in **bin** directory with 
command line arguments to launch MXCuBE. 

.. note::

   Last command line argument has to indicate qt version (**-qt3** or **-qt4**). 

.. code-block:: bash

   Usage: mxcube <GUI definition file> [options] [-qt3 or -qt4]

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
   
   PATH_TO_MXCUBE/bin/mxcube --hardwareRepository=PATH_TO_MXCUBE/ExampleFiles/HardwareObjects.xml -qt4

In this case MXCuBE will start in **Qt4** mode with GUI definition file 
**Qt4_example_mxcube.gui**. It is possible to adjust script by defining gui 
configuration file, additional directories for bricks and hardware objects. For example:

.. code-block:: bash
   
   PATH_TO_MXCUBE/bin/mxcube PATH_TO_GUI_FILE --hardwareRepository=PATH_TO_XML_FILES  --hardwareObjectsDirs=PATHs_TO_ADDITIONAL_HARDWARE_OBJECTS --bricksDirs=PATHS_TO_ADDITIONAL_BRICKS -qt4 

Example xml files are available `here <https://github.com/mxcube/mxcube/tree/master/ExampleFiles/HardwareObjects.xml>`_

3.1. GUI builder
================

GUI builder is used to define GUI layout. It is possible to add, edit or remove bricks, 
change brick parameters, edit signals and slots between bricks. 
To launch gui builder add **-d** before **-qt4** argument. For example:

.. code-block:: bash

   PATH_TO_MXCUBE/bin/mxcube --hardwareRepository=PATH_TO_MXCUBE/ExampleFiles/HardwareObjects.xml -d -qt4

*****************
Other information
*****************

* :doc:`how_to_create_hwobj`
* :doc:`how_to_create_qt_brick`
* :doc:`how_to_define_qt_gui`

