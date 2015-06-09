#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging, sys, traceback
from PyQt4 import QtGui

_handler = None


def Handler():
    """
    Descript. :
    """
    global _handler

    if _handler is None:
        _handler = __Handler()

    return _handler


def disableStdErrRedirection():
    """
    Descript. :
    """
    global _handler
    
    _handler = None

    sys.stderr = sys.__stderr__
    sys.excepthook = sys.__excepthook__
    

def enableStdErrRedirection():
    """
    Descript. : redirect stderr and installs excepthook 
    """
    sys.stderr = Handler()
    sys.excepthook = Handler().excepthook
      

class __Handler:
    """
    Descript. :
    """

    def write(self, buffer):
        """
        Descript. :
        """
        logging.getLogger().error(buffer)
           
    def flush(self):
        """
        Descript. :
        """
        pass

    def excepthook(self, type, value, tb):
        """
        Descript. :
        """
        if type == KeyboardInterrupt:
          #qt.qApp.quit()
          QtGui.QApplication.quit()
          return
        try: 
            exception = traceback.format_exception(type, value, tb)
            logging.getLogger().error('Uncaught exception : ' + '\n'.join(exception))
        except:  
            pass
                    
