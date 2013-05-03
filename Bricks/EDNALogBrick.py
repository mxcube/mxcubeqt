from qt import *
from BlissFramework import BaseComponents
import BlissFramework
import logging

__category__ = 'mxCuBE'

###
###
class EDNATextEdit(QTextEdit):
  COLOR = 'black'

  def __init__(self, *args):
    QTextEdit.__init__(self, *args)
    self.setFont(QFont( "Courier", 10, QFont.Bold ))
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
    self.setTextFormat(QTextEdit.PlainText)
    self.setReadOnly(True)

  def addMessage(self, msg):
    i = msg.find("Characterisation short summary:")
    if i>=0: 
      j = msg.find("-------------------------------", i)
      if j >= 0:
        for l in msg[i:j].split('\n'):
          logging.info(l) 
    self.append(msg)
    self.scrollToBottom()
    
    #self.emit(PYSIGNAL("widgetSynchronize"),(msg,)) 

  #def widgetSynchronize(self, msg):
  #  self.addMessage(msg)


class EDNALogBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('ednaConnection', 'string', '')
        self.addProperty('myTabLabel', 'string', '')

        self.dnaObj=None

        self.defineSlot('addMessage',())
        self.defineSlot('clearMessages',())
        self.defineSlot('tabSelected',())

        self.defineSignal('incUnreadMessages',())
        self.defineSignal('resetUnreadMessages',())

        self.vsplitter = QSplitter(Qt.Vertical,self)

        self.ednaOutputList = QListBox(self.vsplitter)
        self.ednaOutputList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ednaOutputs = {}

        self.ednaOutputBox = QWidgetStack(self.vsplitter)

        QVBoxLayout(self)
        self.layout().addWidget(self.vsplitter)
        #self.layout().addWidget(self.ednaOutputList, 0) 
        #self.layout().addWidget(self.ednaOutputBox, 1)
        #self.vsplitter.addWidget(self.ednaOutputList)
        #self.vsplitter.addWidget(self.ednaOutputBox)

        QObject.connect(self.ednaOutputList, SIGNAL("clicked(QListBoxItem*)"), self.currentListBoxItemChanged)

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'ednaConnection':
            if self.dnaObj is not None:
                self.disconnect(self.dnaObj, PYSIGNAL('displayEdnaMessage'), self.addMessage)
            self.dnaObj=self.getHardwareObject(newValue)
            if self.dnaObj is not None:
                self.connect(self.dnaObj, PYSIGNAL('displayEdnaMessage'), self.addMessage)
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)        

    def addMessage(self,msg, output_file):
        output_widget = self.ednaOutputs.get(output_file)
        if output_widget is None:
          output_widget = EDNATextEdit(self.ednaOutputBox)
          self.ednaOutputBox.addWidget(output_widget)
          self.ednaOutputList.insertItem(output_file)
          self.ednaOutputList.setSelected(len(self.ednaOutputs), True) 
          self.ednaOutputs[output_file]=output_widget
          output_widget.show()
          self.ednaOutputBox.raiseWidget(output_widget)
 
        output_widget.addMessage(msg)

        self.emit(PYSIGNAL("incUnreadMessages"),(1,True,))
       
    def currentListBoxItemChanged(self, item):
        if item is None:
          return
        output_widget = self.ednaOutputs[str(item.text())]
        self.ednaOutputBox.raiseWidget(output_widget)

    def clearMessages(self):
        self.ednaOutputList.clear()
        for output_widget in self.ednaOutputs.itervalues():
          output_widget.clear()
        self.ednaOutputs={}

    def tabSelected(self,tab_name):
        if tab_name==self['myTabLabel']:
            self.emit(PYSIGNAL("resetUnreadMessages"),(True,))
