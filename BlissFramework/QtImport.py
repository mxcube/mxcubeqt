"""

Description
--------------
 
This module import all symbols from PyQt in one single module
space

It also imports the *matplotlib* module and allow to check
version compatibility between PyQt and matplotbil
  
This module, on importing,  assigns the variables:

   qt_imported = [True,False]
   qt_version_no = <list of integers> example:  [4,8,1]
   qt_variant = ['PyQt5','PyQt4','PySide']

   mpl_imported = [True,False]
   mpl_version = <String as provided by matplotlib module>
   mpl_version_no = <list of integers> example:  [1,4,0]

Usage
-------------
This module could be imported directly instead of importing
PyQt.  But the original submodules in PyQt will be flattened.

For example::

   from PyQt4.QtCore import *
   from PyQt4.QtGui import *

   from PyQt5.QtCore import *
   from PyQt5.QtWidgets import *
   from PyQt5.QtGui import *

could be all replaced by::

   from QtImport import *

Or you could directly import things in this way::

  import QtImport as Qt
  app = Qt.QApplication([])

But import lines like::
   from QtImport import Qtcore

would fail (submodules are flattened)

To check the modules you are importing you can
directly use this module to print out a report::

   user@host: python QtImport.py
   Using PyQt:  PyQt4, version: 4.8.6
   Matplotlib:  PyQt4, version: 1.3.1
   Matplotlib is COMPATIBLE with PyQt

  
   

Credits
-------------
Inspired from code from "splot" (http://certif.com)
splot is licensed under LGPL license

"""

import sys

qt_imported = False
qt_variant = None
qt_version_no = []

mpl_imported = False
mpl_version = None
mpl_version_no = False

#
#  Matplotlib import
#
try:
    import matplotlib

    mpl_imported = True
    mpl_version = matplotlib.__version__
    version_parts = mpl_version.split(".")
    mpl_major, mpl_minor = version_parts[:2]
    mpl_version_no = [int(mpl_major), int(mpl_minor), 0]

    if len(version_parts) > 2:
        try:
            import re
            rel = version_parts[2]
            m = re.search("(?P<release>\d+)", rel)
            if m:
                mpl_version_no[2] = int(m.group('release'))
        except:
            pass
except:
    pass

if '--pyqt5' in sys.argv:
    qt_variant = 'PyQt5'
elif '--pyside' in sys.argv:
    qt_variant = 'PySide'
elif '--pyqt4' in sys.argv:
    qt_variant = 'PyQt4'

#
# PyQt5 
#
if (qt_variant == 'PyQt5') or (qt_variant is None and not qt_imported):
    try:
        from PyQt5.QtCore import *
        from PyQt5.QtGui import *
        from PyQt5.QtWidgets import *
        from PyQt5.QtPrintSupport import *
        from PyQt5.uic import *

        getQApp = QCoreApplication.instance

        qt_imported = True
        qt_variant = "PyQt5"
        qt_version_no = list(map(int,QT_VERSION_STR.split(".")))
    except:
        pass
#
# PySide
#
if (qt_variant == 'PySide') or (qt_variant is None and not qt_imported):
    #
    # Maybe you want to try PySide
    #
    try:
        from PySide.QtCore import *
        from PySide.QtGui import *
        from PySide.QtUiTools import *
        from PySide import __version_info__

        pyqtSignal = Signal
        qt_imported = True
        qt_variant = "PySide"
        getQApp = QCoreApplication.instance
        qt_version_no = __version_info__[:3]
        def loadUi(filename, parent=None):
            loader = QUiLoader()
            uifile = QFile(uifilename)
            uifile.open(QFile.ReadOnly)
            ui = loader.load(uifile, parent)
            uifile.close()
            return ui

    except:
        pass

#
# PyQt4
#
if (qt_variant == 'PyQt4') or (qt_variant is None and not qt_imported):
    #
    # Finally try PyQt4 
    #

    # force api 2 (so that the api is common for all pyqt versions)
    #   !! this means the classes below will not exist !!
    # but code is guaranteed to be compatible
    try:
        import sip
        api2_classes = [
            'QData','QDateTime','QString','QTextStream',
            'QTime','QUrl', 'QVariant',
        ]
        for cl in api2_classes:
            try:
                sip.setapi(cl,2)
            except:
                pass

        from PyQt4.QtCore import *
        from PyQt4.QtGui import *
        from PyQt4.uic import *
        
        def getQApp():
            return qApp

        qt_imported = True
        qt_variant = "PyQt4"
        qt_version_no = list(map(int,QT_VERSION_STR.split(".")))
    except:
        pass

#
#  Matplotlib backend assignment
#
if mpl_imported:
    if qt_variant == 'PyQt5':
        if mpl_version_no < [1,4,0]:
            mpl_compat = False
        else:
            mpl_compat = True
            matplotlib.use("Qt5Agg")

    elif qt_variant == 'PySide':
        if mpl_version_no < [1,1,0]:
            mpl_compat = False
        else:
            mpl_compat = True
            matplotlib.use("Qt4Agg")
            from matplotlib import rcParams
            rcParams["backend.qt4"] = "PySide"

    elif qt_variant == 'PyQt4':
        mpl_compat = True
        matplotlib.use("Qt4Agg")

if qt_imported:
    print("Using PyQt:  %s, version: %s" % (qt_variant, "%d.%d.%d" % tuple(qt_version_no)))
else:
    print("Cannot import PyQt")

if mpl_imported:
    print("Matplotlib:  %s, version: %s" % (qt_variant, "%d.%d.%d" % tuple(mpl_version_no)))
else:
    print("Cannot import matplotlib")

if qt_imported and mpl_imported:
    if mpl_compat:
        print("  Matplotlib is COMPATIBLE with PyQt")
    else:
        print("  !!! Matplotlib is NOT COMPATIBLE with PyQt !!!")

