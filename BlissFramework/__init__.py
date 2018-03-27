import gevent.monkey
if not hasattr(gevent, "wait"):
  def mywait(timeout=None):
    return gevent.run(timeout)
  gevent.wait=mywait
import sys
import os
import string
import types

#
# create the root logger
#
import logging

SPLASH_SCREEN = None
def set_splash_screen(screen):
    SPLASH_SCREEN = screen

def get_splash_screen():
    return SPLASH_SCREEN

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s |%(levelname)-7s| %(message)s')


#
# log to stdout
#
_hdlr = logging.StreamHandler(sys.stdout)
_hdlr.setFormatter(_formatter)
logging.getLogger().addHandler(_hdlr)


#
# add the GUI Handler
#
#from Utils import Qt4_GUILogHandler
#_GUIhdlr =Qt4_GUILogHandler.GUILogHandler()

#_logger.addHandler(_GUIhdlr)


#
# Add path to root BlissFramework directory
#
blissframeworkpath = os.path.dirname(__file__)
sys.path.insert(0, blissframeworkpath)


def getStdBricksPath():
    stdbrickspkg = __import__('BlissFramework.Bricks', globals(), locals(), [''])
    return os.path.dirname(stdbrickspkg.__file__)

_bricksDirs = []

def addCustomBricksDirs(bricksDirs):
    import sys

    global _bricksDirs
    
    if type(bricksDirs) == list:
        newBricksDirs = list(filter(os.path.isdir, list(map(os.path.abspath, bricksDirs))))

        for newBrickDir in reversed(newBricksDirs):
            if not newBrickDir in sys.path:
                #print 'inserted in sys.path = %s' % newBrickDir
                sys.path.insert(0, newBrickDir)

        _bricksDirs += newBricksDirs

sys.path.insert(0, getStdBricksPath())
    
def getCustomBricksDirs():
    return _bricksDirs


def _frameworkTraceFunction(frame, event, arg):
    print('EVENT %s' % event)
    print('  { FRAME INFO }')
    print('    - filename  %s' % frame.f_code.co_filename)
    print('    - line      %d' % frame.f_lineno)
    print('    - name      %s' % frame.f_code.co_name)
    

loggingName = ''

def setLoggingName(name, logging_formatter=''):
    global _formatter, _hdlr, loggingName
    logging_formatter.replace(' ', '') 
    if logging_formatter == '':
        logging_formatter = '%(asctime)s |%(name)-7s|%(levelname)-7s| %(message)s'
    _formatter = logging.Formatter(logging_formatter)
    _hdlr.setFormatter(_formatter)

    loggingName = name
    

def setLogFile(filename):
    #
    # log to rotating files
    #
    global _hdlr
    #from logging.handlers import RotatingFileHandler
    from logging.handlers import TimedRotatingFileHandler

    logging.getLogger().info("Logging to file %s" % filename)

    _logger.removeHandler(_hdlr)
        
    #_hdlr = RotatingFileHandler(filename, 'a', 1048576, 10) #1 MB by file, 10 files max.
    _hdlr = TimedRotatingFileHandler(filename, when='midnight', backupCount=1)
    os.chmod(filename, 0o666)
    _hdlr.setFormatter(_formatter)
    _logger.addHandler(_hdlr)

#
# general framework settings
#
_useDumbDbm = False


def setUseDumbDbm(d):
    global _useDumbDbm

    _useDumbDbm = d


def useDumbDbm():
    return _useDumbDbm


def setDebugMode(on):
    if on:
        sys.settrace(_frameworkTraceFunction) 
    else:
        sys.settrace(None)


