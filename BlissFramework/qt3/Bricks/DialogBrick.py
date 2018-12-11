import logging
import types

from qt import *
from BlissFramework.BaseComponents import BlissWidget
from SpecClient_gevent import SpecVariable
 
__category__ = 'General'


class DialogBrick(BlissWidget):    
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
    
        self.flag = False
   
        self.addProperty('specversion', 'string')
        self.addProperty('specWatchVar','string')
        self.specversion = self.specWatchVar = None
        self.setFixedSize(0,0)
        self.hide()
    
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'specversion':
            self.specversion = self.getProperty('specversion').value
        elif propertyName == 'specWatchVar':
            self.specWatchVar = self.getProperty('specWatchVar').value
        if self.specversion != None and self.specWatchVar != None:
            self.myVar = SpecVariable.SpecVariableA(self.specWatchVar, self.specversion, callbacks={"update":self.spec_update})
               
    def spec_update(self, value):
        if not self.flag:
          self.flag = True
          return    
        msgType = value.rsplit(":")[0]
        if not (msgType == 'warning' or msgType == 'question' or msgType == 'information' or msgType == 'critical'):
            msgType = 'warning'
            message = value
        else:
            messageResult = value.rsplit(":")[1:]
        if len(messageResult)==1 or len(messageResult) > 2:
            exec("QMessageBox.%s(self,'Message from Spec (%s)','%s')" % (msgType,self.specversion,messageResult))
            self.answer = None
        elif len(messageResult) == 2:
            resultVariable = messageResult[1]
            message = messageResult[0]
            exec("self.answer = QMessageBox.%s(self,'Message from Spec (%s)','%s')" % (msgType,self.specversion,message))
            """ the following code is an example to set a spec variable to allow the result of a dialog to be known
            and to synchronise in spec when a user has answered a dialog """
            exec("specVar = SpecVariable.SpecVariableA('%s','%s')" %(resultVariable,self.specversion))
            
            if self.myVar.isSpecConnected():
                # set the answer to a non-zero value because by default everything is 0 in spec
                # If this code is improved to allow for more user options then the answer should be set to indicate
                # which answer was given
                self.answer = 1
                specVar.setValue(self.answer)
  
