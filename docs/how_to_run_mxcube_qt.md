## How to install and run MXCuBE Qt version

MXCuBE Qt depends on [mxcubecore](https://github.com/mxcube/mxcubecore) and python should be able to import the mxcubecore package. There are several ways how to run mxcubeqt and one way is to use the environment variables:

- MXCUBE_CORE_CONFIG_PATH : path to the mxcubecore configuration. Can be several paths separated with ":"
- MXCUBE_GUI_CONFIG_PATH: path to the mxcubeqt qui file

```
   git clone https://github.com/mxcube/mxcubecore.git
   git clone https://github.com/mxcube/mxcubeqt.git
   cd mxcubeqt
   pip install requirements_python3.txt or requirements_python2.txt

   export PYTHONPATH=$PYTHONPATH:$(pwd)/mxcubeqt:$(pwd)/mxcubecore
   export MXCUBE_CORE_CONFIG_PATH=$(pwd)/mxcubecore/configuration/mockup/qt:$(pwd)//configuration/mockup/
   export MXCUBE_GUI_CONFIG_PATH=$(pwd)/mxcubeqt/example_config.yml

   python $(pwd)/mxcubeqt/mxcubeqt
```

## Available command line arguments

```
Usage: mxcubeqt <gui definition file> <core configuration paths> [options]

Options:
  -h, --help            show this help message and exit
  --logFile=FILE        Log file
  --logLevel=LOGLEVEL   Log level
  --logTemplate=LOGTEMPLATE
                        Log template
  --bricksDirs=dir1:dir2...dirN
                        Additional directories for bricks search path (you can
                        also use the CUSTOM_BRICKS_PATH environment variable)
  --guiConfigPath=directory
                        Path to the mxcube gui configuration file
                        Alternatively MXCUBE_GUI_CONFIG_PATH env variablecan
                        be used
  --coreConfigPath=GUICONFIGPATH
                        Path to the directory containing mxcubecore
                        configuration files. Alternatively
                        MXCUBE_CORE_CONFIG_PATH env variablecan be used
  --hardwareObjectsDirs=dir1:dir2...dirN
                        Additional directories for Hardware Objects search
                        path (you can also use the
                        CUSTOM_HARDWARE_OBJECTS_PATH environment variable)
  -d                    start GUI in Design mode
  -m                    maximize main window
  --no-border           does not show borders on main window
  --style=APPSTYLE      Visual style of the application (windows, motif,cde,
                        plastique, windowsxp, or macintosh)
  --userFileDir=USERFILEDIR
                        User settings file stores application related settings
                        (window size and position). If not defined then user
                        home directory is used
  -v, --version         Shows version
  --mockupMode          Runs MXCuBE with mockup configuration
  --pyqt4               Force to use PyQt4
  --pyqt5               Force to use PyQt5
  --pyside              Force to use PySide
```

# GUI designer

GUI designer is used to define MXCuBE GUI layout. It is possible to add, edit or remove bricks,
change brick parameters, edit signals and slots between bricks.
To launch gui builder add command line argument **-d**. For example:

```
PATH_TO_MXCUBE/mxcubeqt -d
```

# More information for developers

- [How to create a new hardware object](https://github.com/mxcube/mxcubeqt/tree/master/docs/how_to_create_hwobj.md)
- [How to create a new qt brick](https://github.com/mxcube/mxcubeqt/tree/master/docs/how_to_create_qt_brick.md)
- [How to use gui designer](https://github.com/mxcube/mxcubeqt/tree/master/docs/how_to_define_qt_gui.md)
