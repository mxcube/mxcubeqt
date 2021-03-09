#pylint: skip-file

import sys
from mxcubeqt.utils import qt_import

if qt_import.qt_variant == "PyQt4":
    if sys.version_info[0] == 3:
        from mxcubeqt.utils.QLed.qled_resources_qt4_py3 import *
    else:
        from mxcubeqt.utils.QLed.qled_resources_qt4 import *
elif qt_import.qt_variant == "PyQt5":
    if sys.version_info[0] == 3:
        from mxcubeqt.utils.QLed.qled_resources_qt5_py3 import *
    else:
        from mxcubeqt.utils.QLed.qled_resources_qt5 import *
elif qt_import.qt_variant == "PySide":
    if sys.version_info[0] == 3:
        from mxcubeqt.utils.QLed.qled_resources_pyside_py3 import *
    else:
        from mxcubeqt.utils.QLed.qled_resources_pyside import *
