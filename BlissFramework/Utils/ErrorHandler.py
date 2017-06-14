import logging, sys, traceback
import qt

_handler = None


def Handler():
    global _handler

    if _handler is None:
        _handler = __Handler()

    return _handler


def disableStdErrRedirection():
    global _handler
    
    _handler = None

    sys.stderr = sys.__stderr__
    sys.excepthook = sys.__excepthook__
    

def enableStdErrRedirection():
    #
    # redirect stderr and installs excepthook 
    #
    sys.stderr = Handler()
    sys.excepthook = Handler().excepthook
      

class __Handler:
    def write(self, buffer):
        logging.getLogger().error(buffer)
           
 
    def flush(self):
        pass

    
    def excepthook(self, type, value, tb):
        if type == KeyboardInterrupt:
          qt.qApp.quit()
          return
        try: 
            exception = traceback.format_exception(type, value, tb)
            logging.getLogger().error('Uncaught exception : ' + '\n'.join(exception))
        except:  
            pass
                    
