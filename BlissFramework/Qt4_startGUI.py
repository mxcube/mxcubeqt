#!/usr/bin/env python 

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

import gevent
import time
import fcntl
import tempfile
import socket
import sys
import os
import logging
import traceback
from optparse import OptionParser

from PyQt4 import QtCore
from PyQt4 import QtGui

import BlissFramework
from BlissFramework import Qt4_GUISupervisor
from BlissFramework.Utils import Qt4_ErrorHandler
from BlissFramework.Utils import Qt4_GUILogHandler

#from BlissFramework.Utils import terminal_server

from HardwareRepository import HardwareRepository

_logger = logging.getLogger()
_GUIhdlr = Qt4_GUILogHandler.GUILogHandler()
_logger.addHandler(_GUIhdlr)


def do_gevent():
    """
    Descript.  can't call gevent.run inside inner event loops (message boxes...)
    """
    if QtCore.QEventLoop():
        try:
          gevent.wait(timeout=0.01)
        except AssertionError:
          pass
    else:
        # all that I tried with gevent here fails! => seg fault
        pass

class MyCustomEvent(QtCore.QEvent):
    """
    Descript. : 
    """

    def __init__(self, event_type, data):
        """
        Descript. : 
        """
        QtCore.QEvent.__init__(self, event_type)
        self.data = data     

def run(GUIConfigFile = None):    
    """
    Descript. : 
    """

    defaultHwrServer = 'localhost:hwr'
    userHomeDir = os.path.expanduser("~") #path to user's home dir. (works on Win2K, XP, Unix, Mac...) 

    parser = OptionParser(usage = 'usage: %prog <GUI definition file> [options]')
    parser.add_option('', '--logFile', action = 'store', type = 'string', 
                      help = 'Log file', dest = 'logFile', metavar = 'FILE', default = '')
    parser.add_option('', '--logLevel', action = 'store', type = 'string', 
                      help = 'Log level', dest = 'logLevel', default = 'INFO')
    parser.add_option('', '--bricksDirs', action = 'store', type = 'string', 
                      help = 'Additional directories for bricks search path (you can also use the CUSTOM_BRICKS_PATH environment variable)', 
                      dest = 'bricksDirs', metavar = 'dir1'+os.path.pathsep+'dir2...dirN', default = '')
    parser.add_option('', '--hardwareRepository', action = 'store', type = 'string', 
                      help = 'Hardware Repository Server host:port (default to %s) (you can also use HARDWARE_REPOSITORY_SERVER the environment variable)' % defaultHwrServer, 
                      metavar = 'HOST:PORT', dest = 'hardwareRepositoryServer', default = '')                   
    parser.add_option('', '--hardwareObjectsDirs', action = 'store', type = 'string', 
                      help = 'Additional directories for Hardware Objects search path (you can also use the CUSTOM_HARDWARE_OBJECTS_PATH environment variable)', 
                      dest = 'hardwareObjectsDirs', metavar = 'dir1' + os.path.pathsep + 'dir2...dirN', 
                      default = '')
    parser.add_option('-d', '', action='store_true', dest="designMode", 
                      default=False, help="start GUI in Design mode")
    parser.add_option('-m', '', action='store_true', dest="showMaximized", 
                      default=False, help="maximize main window")	
    parser.add_option('', '--no-border', action='store_true', dest='noBorder', 
                      default=False, help="does not show borders on main window")
    #parser.add_option('-s', '--syle', action='store', type="string", dest='style', default=0, help="GUI style")
    parser.add_option('-w', '--web-server-port', action='store', type="int", 
                      dest='webServerPort', default=0, help="port number for the remote interpreter web application server")
    #parser.add_option('', '--widgetcount', action='store_true', dest='widgetCount', default=False, help="prints debug message at the end about number of widgets left undestroyed")

    (opts, args) = parser.parse_args()
    
    if len(args) >= 1:
        if len(args) == 1:
            GUIConfigFile = os.path.abspath(args[0])
        else:
            parser.error('Too many arguments.')
            sys.exit(1)

    """if opts.webServerPort:
        interpreter = terminal_server.InteractiveInterpreter()
        terminal_server.set_interpreter(interpreter) 
        gevent.spawn(terminal_server.serve_forever, opts.webServerPort)"""

    #
    # get config from arguments
    #
    logFile = opts.logFile        
    hoDirs = opts.hardwareObjectsDirs.split(os.path.pathsep)
    bricksDirs = opts.bricksDirs.split(os.path.pathsep)

    if opts.hardwareRepositoryServer:
      hwrServer = opts.hardwareRepositoryServer
    else:
      #
      # try to set Hardware Repository server from environment
      #
      try:
          hwrServer = os.environ['HARDWARE_REPOSITORY_SERVER']
      except KeyError:
          hwrServer = defaultHwrServer

    #
    # add bricks directories and hardware objects directories from environment
    #
    try:
        bricksDirs += os.environ['CUSTOM_BRICKS_PATH'].split(os.path.pathsep)
    except KeyError:
        pass
    
    try:
        hoDirs += os.environ['CUSTOM_HARDWARE_OBJECTS_PATH'].split(os.path.pathsep)
    except KeyError:
        pass

    bricksDirs = filter(None, bricksDirs)
    hoDirs = filter(None, hoDirs)
    
    app = QtGui.QApplication([])
    lockfile = None

    if not opts.designMode and GUIConfigFile: 
      lock_filename=os.path.join(tempfile.gettempdir(), '.%s.lock' % os.path.basename(GUIConfigFile or "unnamed"))
      try:
          lockfile = open(lock_filename, "w")
      except:
          logging.getLogger().exception("Cannot create lock file (%s), exiting" % lock_filename)

          sys.exit(1)
      else:
          os.chmod(lock_filename,0666)
          try:
             fcntl.lockf(lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
          except:
             logging.getLogger().exception("Cannot acquire lock (%s), exiting (hint: maybe the same application is already running ?)" % lock_filename)
           
             sys.exit(1)
    
    #
    # configure modules
    #
    HardwareRepository.setHardwareRepositoryServer(hwrServer)
    HardwareRepository.addHardwareObjectsDirs(hoDirs)
    BlissFramework.addCustomBricksDirs(bricksDirs)
    
    #
    # set log name and log file
    #
    if GUIConfigFile:
        BlissFramework.setLoggingName(os.path.basename(GUIConfigFile))

    log_lockfile = None
    if len(logFile) > 0:
      log_lock_filename=os.path.join(tempfile.gettempdir(), '.%s.lock' % os.path.basename(logFile))

      log_ok=True
      try:
          log_lockfile = open(log_lock_filename, "w")
      except:
          log_ok=False
      else:
          try:
            os.chmod(log_lock_filename,0666)
          except:
            pass
          try:
             fcntl.lockf(log_lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
          except:
             log_ok=False
             try:
               log_lockfile.close()
             except:
               pass

      if not log_ok:
        i=1
        logfile_details=os.path.splitext(logFile)
        logFile=""
        while i<10:
          logFile2="%s.%d%s" % (logfile_details[0],i,logfile_details[1])
          log_lock_filename2=os.path.join(tempfile.gettempdir(), '.%s.lock' % os.path.basename(logFile2))
          try:
            log_lockfile = open(log_lock_filename2, "w")
          except:
            pass
          else:
            try:
              os.chmod(log_lock_filename2,0666)
            except:
              pass
            try:
               fcntl.lockf(log_lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except:
               pass
            else:
              log_ok=True
          if log_ok:
            logFile=logFile2
            break
          i+=1

      if len(logFile) > 0:
        BlissFramework.setLogFile(logFile)

    #
    # log startup details
    #
    logLevel = getattr(logging, opts.logLevel)
    logging.getLogger().setLevel(logLevel)
    logInfo = 'Qt4 GUI started (%s)' % (GUIConfigFile or "unnamed")
    logInfo += ', HWRSERVER=%s' % hwrServer
    if len(hoDirs) > 0:
        logInfo += ', HODIRS=%s' % os.path.pathsep.join(hoDirs)
    if len(bricksDirs) > 0:
        logInfo += ', BRICKSDIRS=%s' % os.path.pathsep.join(bricksDirs)
    logging.getLogger().info(logInfo)

    QtGui.QApplication.setDesktopSettingsAware(False) #use default settings
    QtCore.QObject.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app.quit)
   
    supervisor = Qt4_GUISupervisor.GUISupervisor(designMode = opts.designMode, showMaximized=opts.showMaximized, noBorder=opts.noBorder)

    #BlissFramework.setDebugMode(True)
    #
    # post event for GUI creation
    #
    #pp.postEvent(supervisor, QtCore.QEvent(Qt4_GUISupervisor.LOAD_GUI_EVENT, GUIConfigFile))
    app.postEvent(supervisor, MyCustomEvent(Qt4_GUISupervisor.LOAD_GUI_EVENT, GUIConfigFile))
        
    #
    # redirect errors to logger
    #
    Qt4_ErrorHandler.enableStdErrRedirection()

    gevent_timer = QtCore.QTimer()
    gevent_timer.connect(gevent_timer, QtCore.SIGNAL("timeout()"), do_gevent)
    gevent_timer.start(0)

    app.setOrganizationName("MXCuBE")
    app.setOrganizationDomain("https://github.com/mxcube")
    app.setApplicationName("MXCuBE")
    #app.setWindowIcon(QIcon("images/icon.png"))
    app.exec_()



    """
    def process_qt_events():
      while True:
        time.sleep(0.01)
        while app.hasPendingEvents():
          app.processEvents() 
          time.sleep(0.01)
          if not app.mainWidget() or not app.mainWidget().isVisible():
            return
    qt_events = gevent.spawn(process_qt_events) 
    qt_events.join()   
    """

    supervisor.finalize()

    if lockfile is not None:
        filename = lockfile.name
        try:
            lockfile.close()
            os.unlink(filename)
        except:
            logging.getLogger().error("Problem removing the lock file")

    if log_lockfile is not None:
        filename = log_lockfile.name
        try:
            log_lockfile.close()
            os.unlink(filename)
        except:
            logging.getLogger().exception("Problem removing the log lock file")


if __name__ == '__main__':
    run()
