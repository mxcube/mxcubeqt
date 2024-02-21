#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import sys
import logging
import traceback

from mxcubeqt.utils import qt_import

_handler = None


def Handler():
    global _handler

    if _handler is None:
        _handler = __Handler()

    return _handler


def disable_std_err_redirection():
    global _handler

    _handler = None

    sys.stderr = sys.__stderr__
    sys.excepthook = sys.__excepthook__


def enable_std_err_redirection():
    """
    Descript. : redirect stderr and installs excepthook
    """
    sys.stderr = Handler()
    sys.excepthook = Handler().excepthook


class __Handler:

    def write(self, buffer):
        logging.getLogger().error(buffer)

    def flush(self):
        pass

    def excepthook(self, type, value, tb):
        logging.getLogger("HWR").debug(f"  exception hook. quitting {value}")
        logging.getLogger("HWR").debug(f"{tb}")

        if type == KeyboardInterrupt:
            qt_import.getQApp().quit()
            return

        try:
            exception = traceback.format_exception(type, value, tb)
            logging.getLogger().error("Uncaught exception : " + "\n".join(exception))
        except BaseException:
            pass
