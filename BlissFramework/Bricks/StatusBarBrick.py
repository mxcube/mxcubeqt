from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Utils import widget_colors
from qt import *
import logging
from widgets.spin_box_buttons import SpinBoxButtons

'''

Doc please...

'''

__category__ = 'GuiUtils'

class StatusBarBrick(BlissWidget):
    STATES = { "Unknown": QWidget.gray,\
        "Disconnected": widget_colors.LIGHT_RED,\
        "Connected": QColor(255,165,0),\
        "Busy": QWidget.yellow,\
        "Ready": widget_colors.LIGHT_GREEN }

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)
        self.specStateHO=None
        self.statusBar=None
        
        self.specStateLabel=None

        self.addProperty('specstate','string','')
        self.addProperty('statusSearchDepth','integer',3)

        self.defineSlot('setMessage',())

        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        # Information messages
        self.MAX_BUFFER_SIZE = 5
        self.messages = []
        self.read_idx = 0
        self.insert_idx = 0

        self.button = QPushButton("Add", self, "add_button")
        self.v_scroll = SpinBoxButtons(self, 'v_scroll')
        
        QObject.connect(self.v_scroll, PYSIGNAL("scroll_up"), 
                        self.next_message)
        QObject.connect(self.v_scroll, PYSIGNAL("scroll_down"), 
                        self.prev_message)

    def next_message(self):
        if self.read_idx < self.MAX_BUFFER_SIZE - 1:
            self.read_idx += 1
            self.statusBar.message(self.messages[self.read_idx]) 

    
    def prev_message(self):
        if self.read_idx > 0:
            self.read_idx -= 1
            self.statusBar.message(self.messages[self.read_idx]) 


    def findMenu(self,top_widget,depth_level):
        if depth_level==0:
            return None
        child_list=top_widget.children()
        if child_list is not None:
            for w in child_list:
                if isinstance(w,QStatusBar):
                    return w
                menu=self.findMenu(w,depth_level-1)
                if menu is not None:
                    return menu

    def setMessage(self, message):
        if self.isRunning():
            if self.statusBar is not None:
                self.messages.insert(self.insert_idx, message)
                self.statusBar.message(message)
                self.read_idx = self.insert_idx
                self.insert_idx = (self.insert_idx + 1) % self.MAX_BUFFER_SIZE
            

    def specStateChanged(self,state, spec_version):
        if self.isRunning():
            if self.specStateLabel is None:
                return
            try:
                color=self.STATES[state]
            except KeyError:
                state='Unknown'
                color=self.STATES[state]
            self.specStateLabel.setPaletteBackgroundColor(QColor(color))

    def run(self):
        top_widget=qApp.mainWidget()

        search_depth=self['statusSearchDepth']
        self.statusBar=self.findMenu(top_widget,search_depth)
        if self.statusBar is not None:
            f=self.statusBar.font()
            f.setPointSize(self.font().pointSize())
            self.statusBar.setFont(f)

            self.statusBar.addWidget(self.v_scroll, 0, True)

            if self.specStateHO is not None:
                try:
                    version=self.specStateHO.getVersion()[1]
                except:
                    logging.getLogger().exception("StatusBarBrick: could not get spec version")
                else:
                    self.specStateLabel=QLabel("spec: %s" % version,self.statusBar)
                    self.statusBar.addWidget(self.specStateLabel,0,True)
                    self.specStateChanged(*self.specStateHO.getState())

            self.setMessage("One")
            self.setMessage("Two")
            self.setMessage("Three")        
            self.setMessage("Four")
            self.setMessage("Ready")
        else:
            logging.getLogger().debug("StatusBarBrick: could not find the windows's status bar")

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='specstate':
            if self.specStateHO is not None:
                self.disconnect(self.specStateHO,'specStateChanged',self.specStateChanged)
            self.specStateHO=self.getHardwareObject(newValue)
            if self.specStateHO is not None:
                self.connect(self.specStateHO,'specStateChanged',self.specStateChanged)
        else:
            BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)
