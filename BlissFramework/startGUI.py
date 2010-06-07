#!/usr/bin/env python 

import fcntl
import tempfile
import socket
import sys
import os
import logging
from optparse import OptionParser

from qt import *

import BlissFramework
from BlissFramework import GUISupervisor
from BlissFramework.Utils import ErrorHandler

from HardwareRepository import HardwareRepository

if __name__ == '__main__':    
    defaultHwrServer = socket.gethostname() + ':hwr'
    userHomeDir = os.path.expanduser("~") #path to user's home dir. (works on Win2K, XP, Unix, Mac...) 

    parser = OptionParser(usage = 'usage: %prog <GUI definition file> [options]')
    parser.add_option('', '--no-opengl', action="store_true", dest="disableOpenGL", default=False, help="Disable OpenGL support")
    parser.add_option('', '--logFile', action = 'store', type = 'string', help = 'Log file', dest = 'logFile', metavar = 'FILE', default = '')
    parser.add_option('', '--bricksDirs', action = 'store', type = 'string', help = 'Additional directories for bricks search path (you can also use the CUSTOM_BRICKS_PATH environment variable)', dest = 'bricksDirs', metavar = 'dir1'+os.path.pathsep+'dir2...dirN', default = '')
    parser.add_option('', '--hardwareRepository', action = 'store', type = 'string', help = 'Hardware Repository Server host:port (default to %s) (you can also use HARDWARE_REPOSITORY_SERVER the environment variable)' % defaultHwrServer, metavar = 'HOST:PORT', dest = 'hardwareRepositoryServer', default = '')                   
    parser.add_option('', '--hardwareObjectsDirs', action = 'store', type = 'string', help = 'Additional directories for Hardware Objects search path (you can also use the CUSTOM_HARDWARE_OBJECTS_PATH environment variable)', dest = 'hardwareObjectsDirs', metavar = 'dir1'+os.path.pathsep+'dir2...dirN', default = '')
    parser.add_option('-x', '', action='store_true', dest="executionOnly", default=False, help="start GUI for execution only (no switch to design mode, no reload available)")
    parser.add_option('-d', '', action='store_true', dest="designMode", default=False, help="start GUI in Design mode")
    parser.add_option('-m', '', action='store_true', dest="showMaximized", default=False, help="maximize main window")	
    parser.add_option('', '--no-border', action='store_true', dest='noBorder', default=False, help="does not show borders on main window")
    #parser.add_option('', '--widgetcount', action='store_true', dest='widgetCount', default=False, help="prints debug message at the end about number of widgets left undestroyed")

    (opts, args) = parser.parse_args()
    GUIConfigFile = None
    
    if len(args) >= 1:
        if len(args) == 1:
            GUIConfigFile = os.path.abspath(args[0])
        else:
            parser.error('Too many arguments.')
            sys.exit(1)

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
    
    app = QApplication([])
    lockfile = None

    if not opts.designMode and GUIConfigFile: 
      lock_filename=os.path.join(tempfile.gettempdir(), '.%s.lock' % os.path.basename(GUIConfigFile or "unnamed"))
      try:
          lockfile = open(lock_filename, "w")
      except:
          logging.getLogger().exception("Cannot create lock file (%s), exiting" % lock_filename)

          sys.exit(1)
      else:
          os.chmod(lock_filename,666)
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
    # set OpenGL support
    #
    BlissFramework.setOpenGLEnabled(not opts.disableOpenGL)

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
            os.chmod(log_lock_filename,666)
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
              os.chmod(log_lock_filename2,666)
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
    logInfo = 'GUI started (%s)' % (GUIConfigFile or "unnamed")
    logInfo += ', HWRSERVER=%s' % hwrServer
    if len(hoDirs) > 0:
        logInfo += ', HODIRS=%s' % os.path.pathsep.join(hoDirs)
    if len(bricksDirs) > 0:
        logInfo += ', BRICKSDIRS=%s' % os.path.pathsep.join(bricksDirs)
    logging.getLogger().info(logInfo)

    QApplication.setDesktopSettingsAware(False) #use default settings
   
    supervisor = GUISupervisor.GUISupervisor(executionOnly = opts.executionOnly, designMode = opts.designMode, showMaximized=opts.showMaximized, noBorder=opts.noBorder)

    QObject.connect(app, SIGNAL("aboutToQuit()"), supervisor.finalize)
    QObject.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))

    #BlissFramework.setDebugMode(True)
    #
    # post event for GUI creation
    #
    app.postEvent(supervisor, QCustomEvent(GUISupervisor.LOAD_GUI_EVENT, GUIConfigFile))
        
    #
    # redirect errors to logger
    #
    ErrorHandler.enableStdErrRedirection()
    
    app.exec_loop()
    
    if lockfile is not None:
        filename = lockfile.name
        try:
            lockfile.close()
            os.unlink(filename)
        except:
            logging.getLogger().exception("Problem removing the lock file")

    if log_lockfile is not None:
        filename = log_lockfile.name
        try:
            log_lockfile.close()
            os.unlink(filename)
        except:
            logging.getLogger().exception("Problem removing the log lock file")
