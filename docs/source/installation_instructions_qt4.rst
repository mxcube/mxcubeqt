How to install and run Qt version of MXCuBE
=====================

MXCuBE is organized as a subset of several git submodules that are necessary to run MXCuBE. 
In this page a sequence how to get software code, install dependencies and execute software is described.

MXCuBE has been tested with:

* Linux: Ubuntu 10, 12, 14 (with gnome and kde) and Centos
* Macos.

Git repository
--------------

The MxCuBE is hosten in several git projects that all together can be found `here <https://github.com/mxcube/mxcube>`_
The repository is organized in three submodules:

* `HardwareRepository <https://github.com/mxcube/HardwareRepository.git>`_
* `HardwareObjects <https://github.com/mxcube/HardwareObjects.git>`_
* `BlissFramework <https://github.com/mxcube/BlissFramework.git>`_

To get MXCuBE code execute:

.. code-block:: bash

   git clone https://github.com/mxcube/mxcube.git mxcube-2
   cd mxcube-2
   git submodule init
   git submodule update

Python dependencies
-------------------

* `Python (>2.6) <https://www.python.org/>`_
* `Qt4 <http://doc.qt.io/qt-4.8/)>`_
* `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_ 
* `louie (pydispatcher) <https://pypi.python.org/pypi/Louie/1.1>`_
* `gevent >= 1.0RC2 <https://github.com/downloads/surfly/gevent/gevent-1.0rc2.tar.gz>`_
* `PyChooch <http://github.com/mxcube/pychooch>`_
* `PyMca <http://sourceforge.net/projects/pymca/>`_
* `jsonpickle <https://pypi.python.org/pypi/jsonpickle/0.7.0>`_
* `scipy stack <http://www.scipy.org/install.html>`_

If Ubuntu/Debian used then dependecies can be installed with command:

.. code-block:: bash

   sudo apt-get install python-qt4, python-gevent, python-louie, python-jsonpickle, python-numpy, python-scipy, python-matplotlib, python-suds, pymca 

Running code
------------

Use mxcube script located in bin directory to launch MXCuBE. It is possible to use command line arguments to adjust MXCuBE. 

.. note::

   Last command line argument has to indicate qt version (-qt3 or -qt4). 

.. code-block:: bash

   Usage: mxcube <GUI definition file> [options] [-qt3 or -qt4]

   Options:
	  -h, --help            show this help message and exit
	  --logFile=FILE        Log file
	  --logLevel=LOGLEVEL   Log level
	  --bricksDirs=dir1:dir2...dirN
	               Additional directories for bricks search path (you can
                       also use the CUSTOM_BRICKS_PATH environment variable)
	  --hardwareRepository=HOST:PORT
                               Hardware Repository Server host:port (default to
                    	       localhost:hwr) (you can also use
	                       HARDWARE_REPOSITORY_SERVER the environment variable)
	  --hardwareObjectsDirs=dir1:dir2...dirN
        	                Additional directories for Hardware Objects search
                	        path (you can also use the
                        	CUSTOM_HARDWARE_OBJECTS_PATH environment variable)
	  -d                    start GUI in Design mode
	  -m                    maximize main window
	  --no-border           does not show borders on main window

run_mxcube.csh script located in bin directory can be adjusted. For example to run MXCuBE with default parameters edit script:

.. code-block:: bash
   
   PATH_TO_MXCUBE/bin/mxcube --hardwareRepository=PATH_TO_MXCUBE/ExampleFiles/HardwareObjects.xml -qt4

In this case MXCuBE will start in Qt4 mode with GUI definition file Qt4_example_mxcube.gui.
It is possible to adjust script by defining gui configuration file, additional directories for bricks and hardware objects. For example:

.. code-block:: bash
   
   PATH_TO_MXCUBE/bin/mxcube PATH_TO_GUI_FILE --hardwareRepository=PATH_TO_XML_FILES  --hardwareObjectsDirs=PATHs_TO_ADDITIONAL_HARDWARE_OBJECTS --bricksDirs=PATHS_TO_ADDITIONAL_BRICKS -qt4 

Example xml files are available `here <https://github.com/mxcube/mxcube/tree/master/ExampleFiles/HardwareObjects.xml>`_

GUI builder
-----------

GUI builder is used to define GUI layout. It is possible to add, edit or remove bricks, change brick parameters, edit signals and slots between bricks. To launch gui builder add -d before -qt4 argument. For example:

.. code-block:: bash

   PATH_TO_MXCUBE/bin/mxcube --hardwareRepository=PATH_TO_MXCUBE/ExampleFiles/HardwareObjects.xml -d -qt4
