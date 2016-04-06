import qt
import logging
import sys

from BlissFramework.BaseComponents import BlissWidget
from MultiAxisAlignmentBrick import MultiAxisAlignmentBrick
from BlissFramework.Utils import widget_colors

__category__ = "Motor"

class MultiplePositionsBrick(BlissWidget):
    colorState = {
        'NOTINITIALIZED': widget_colors.LIGHT_RED, 
        'UNUSABLE': widget_colors.LIGHT_RED,
        'READY': widget_colors.LIGHT_GREEN,
        'MOVING': widget_colors.LIGHT_YELLOW,
        }
    nameState = ['READY', 'MOVING', 'UNUSABLE', 'NOTINITIALIZED']
    
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)

        """
        variables
        """
        self.__brickStarted = False
        self.__lastPosition = None
        
        """
        properties
        """
        self.addProperty('appearance', "combo",
                        ("Display", "Move", "Configure", "Incremental"), "Move")
        self.appearance = None
        self.addProperty('mnemonic', 'string')
        self.hwro = None
        self.addProperty('check', 'boolean', False)
        self.checkMove = None

        """
        signals
        """
        self.defineSignal("clicked", ())
        self.defineSlot("setEnabled", ())
        
        """
        interface
        """
        self.buildInterface()
            
    def buildInterface(self):        
        self.layout = qt.QHBoxLayout(self)
        
        self.titleLabel = QubLabel("<B>Title<B>", self)
        self.titleLabel.setAlignment(qt.Qt.AlignCenter)
        self.titleLabel.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Expanding,
                                           qt.QSizePolicy.Fixed))
        self.layout.addWidget(self.titleLabel)
        
        """
        move and configure appearence
        """
        self.radioGroup = QubRadioGroup(QubRadioGroup.Horizontal, self)
        self.radioGroup.hide()
        self.connect(self.radioGroup, qt.PYSIGNAL("PositionClicked"),
                     self.positionClicked)
        self.layout.addWidget(self.radioGroup)
                
        self.setButton = qt.QPushButton("Set", self)
        self.setButton.hide()
        self.connect(self.setButton, qt.SIGNAL("clicked()"),
                     self.setPosition)
        self.setButton.setEnabled(False)
        self.layout.addWidget(self.setButton)
                
        """
        display appearence
        """     
        self.valueLabel = qt.QLabel("no value", self)
        self.valueLabel.hide()
        self.valueLabel.setAlignment(qt.Qt.AlignCenter)
        self.layout.addWidget(self.valueLabel)               

        """
        incremental appearence
        """
        self.frame = qt.QFrame(self)
        self.frame.hide()
        self.frame.setFrameShape(qt.QFrame.NoFrame)
        self.frame.setFrameShadow(qt.QFrame.Plain)
        self.layout.addWidget(self.frame)
        
        vlayout = qt.QVBoxLayout(self.frame)
        vlayout.setMargin(10)
                
        self.valueWidget = QubValue(self.frame, titleType=QubValue.Label,
                                   valueType=QubValue.Label,
                                   orientation=QubValue.Horizontal)
        self.valueWidget.setTitle("Current Position")
        vlayout.addWidget(self.valueWidget)
        
        vlayout.addSpacing(5)
        
        hlayout = qt.QHBoxLayout(vlayout)
        
        self.positionList = qt.QListBox(self.frame)
        hlayout.addWidget(self.positionList)
        
        hlayout.addSpacing(5)
        
        vlayout1 = qt.QVBoxLayout(hlayout)
        
        self.gotoButton = qt.QPushButton("Go", self.frame)
        self.connect(self.gotoButton, qt.SIGNAL("clicked()"),
                     self.gotoPosition)
        vlayout1.addWidget(self.gotoButton)
        
        vlayout1.addStretch(1)
        
        self.addButton = qt.QPushButton("Add", self.frame)
        self.connect(self.addButton, qt.SIGNAL("clicked()"),
                     self.addPosition)
        vlayout1.addWidget(self.addButton)
        
        vlayout1.addSpacing(5)
        
        self.remButton = qt.QPushButton("Delete", self.frame)
        self.connect(self.remButton, qt.SIGNAL("clicked()"),
                     self.remPosition)
        vlayout1.addWidget(self.remButton)
        
        """
        popup config
        """
        self.configWindow = MultiplePositionConfigurator(self)
        self.popupMenu = qt.QPopupMenu(self.titleLabel)
        self.popupMenu.insertItem("Configure", self.configWindow.show)
        
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            #self.configWindow.clearConfigurator()
            #self.disconnectHardwareObject()
            #if self.hwro is not None:
            #    self.radioGroup.clearRadioList()
            #self.__lastPosition = None
            if self.hwro is None:
              self.hwro = self.getHardwareObject(newValue)
              if self.__brickStarted:
                self.hardwareObjectChange(self.hwro)
            else:
              self.hwro = self.getHardwareObject(newValue)
        if property == 'appearance':
            self.appearance = newValue
            if self.__brickStarted:
                self.appearanceChange(self.appearance)

        if property == 'check':
            self.checkMove = newValue
    
    def run(self):
        self.hardwareObjectChange(self.hwro)
        self.__brickStarted = True
        
    def hardwareObjectChange(self, hwro):
        self.connectHardwareObject()
        self.positionList.clear()

        if self.hwro is not None:
            title = "<B>"+self.hwro.username.replace(" ", "&nbsp;")+"<B>"                             
            self.titleLabel.setText(title)

            for key in self.hwro.positionsIndex:
                self.radioGroup.addRadio(str(key))
                self.positionList.insertItem(str(key))
        else:
            self.titleLabel.setText("<B>Unknown<B>")
            self.valueLabel.setText("no value")
            self.valueWidget.setValue("no value")

        self.configWindow.setHardwareObject(self.hwro)

        self.appearanceChange(self.appearance)
            
    def appearanceChange(self, appearance):
        try:
            self.appearance = appearance

            if self.appearance == "Move" or \
               self.appearance == "Configure" or \
               self.appearance == "Incremental":
               
                self.valueLabel.hide()

                if self.appearance == "Move" or \
                   self.appearance == "Configure":
                   
                    self.titleLabel.setPopup(self.popupMenu)
                    self.radioGroup.show()
                    if self.appearance == "Configure":
                        self.setButton.show()
                    else:
                        self.setButton.hide()
                else:
                    self.setButton.hide()
                    self.configWindow.hide()
                    self.radioGroup.hide()
                    self.frame.show()
                    

            if self.appearance == "Display":
                self.titleLabel.setPopup(None)
                self.radioGroup.hide()
                self.setButton.hide()
                self.configWindow.hide()
                self.frame.hide()

                self.valueLabel.show()

            if self.hwro is not None and self.hwro.isReady():
                self.equipmentReady()
                self.hwro.checkPosition() 
                self.checkState() 
            else:
                self.equipmentNotReady()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])
    
    def connectHardwareObject(self):
        if self.hwro is not None:                               
            self.connect(self.hwro, qt.PYSIGNAL("positionReached"),
                             self.positionChanged)
            self.connect(self.hwro, qt.PYSIGNAL("noPosition"),
                             self.noPosition)
            self.connect(self.hwro, qt.PYSIGNAL("stateChanged"),
                             self.checkState)
            self.connect(self.hwro, qt.PYSIGNAL("equipmentReady"),
                             self.equipmentReady)
            self.connect(self.hwro, qt.PYSIGNAL("equipmentNotReady"),
                             self.equipmentNotReady)
    
    def disconnectHardwareObject(self):

        if self.hwro is not None:
            self.disconnect(self.hwro, qt.PYSIGNAL("positionReached"),
                                self.positionChanged)
            self.disconnect(self.hwro, qt.PYSIGNAL("noPosition"),
                                self.noPosition)
            self.disconnect(self.hwro, qt.PYSIGNAL("stateChanged"),
                                self.checkState)
            self.disconnect(self.hwro, qt.PYSIGNAL("equipmentReady"),
                                self.equipmentReady)
            self.disconnect(self.hwro, qt.PYSIGNAL("equipmentNotReady"),
                                self.equipmentNotReady)

    def equipmentReady(self):
        self.setEnabled(True)
            
        if self.appearance == "Display":
            qcolor = qt.QColor(MultiplePositionsBrick.colorState["READY"])
            self.valueLabel.setPaletteBackgroundColor(qcolor)
        else:
            qcolor = qt.QColor(MultiplePositionsBrick.colorState["READY"])
            self.titleLabel.setPaletteBackgroundColor(qcolor)
            
        if self.appearance == "Incremental":
            self.gotoButton.setEnabled(True)
            
    def equipmentNotReady(self):
        self.setEnabled(False)
            
        if self.appearance == "Display":
            qcolor = qt.QColor(MultiplePositionsBrick.colorState["NOTINITIALIZED"])
            self.valueLabel.setPaletteBackgroundColor(qcolor)
        else:
            qcolor = qt.QColor(MultiplePositionsBrick.colorState["NOTINITIALIZED"])
            self.titleLabel.setPaletteBackgroundColor(qcolor)
            
        if self.appearance == "Incremental":
            self.gotoButton.setEnabled(False)
        
    def positionClicked(self, name):
        if self.hwro is not None:
            if self.checkMove:
                msgstr  = "You will move \"%s\" to position \"%s\"" %(self.hwro.username,name)
                ret = qt.QMessageBox.warning(None, "Move to position", msgstr,
                                    qt.QMessageBox.Ok,
                                    qt.QMessageBox.Cancel,
                                    qt.QMessageBox.NoButton)
                                   
                if ret == qt.QMessageBox.Ok:
                    self.hwro.moveToPosition(name)
                else:
                    self.hwro.checkPosition() 
            else:
                self.hwro.moveToPosition(name)
            
    def positionChanged(self, name):
        if self.appearance == "Move" or self.appearance == "Configure":
            self.radioGroup.setChecked(name, True)
            if self.appearance == "Configure":
                self.__lastPosition = name
                self.setButton.setEnabled(True)
                self.setButton.setText("Set \"%s\""%name)
            
        if self.appearance == "Display":
            self.valueLabel.setText(name)
            
        if self.appearance == "Incremental":
            self.valueWidget.setValue(name)

    def noPosition(self):
        if self.appearance == "Move" or self.appearance == "Configure":
            self.radioGroup.deselectAll()
            
        if self.appearance == "Display":
            state = self.hwro.getState()
            if state == "MOVING":
                self.valueLabel.setText("Moving")
            else :
                self.valueLabel.setText("Unknown")
            
        if self.appearance == "Incremental":
            state = self.hwro.getState()
            if state == "MOVING":
                self.valueWidget.setValue("Moving")
            else :
                self.valueWidget.setValue("Unknown")

    def checkState(self, _=None):
        state = self.hwro.getState()
        
        if state in MultiplePositionsBrick.nameState:
            qcolor = qt.QColor(MultiplePositionsBrick.colorState[state])
            if self.appearance == "Display":
                self.valueLabel.setPaletteBackgroundColor(qcolor)
            else:
                self.titleLabel.setPaletteBackgroundColor(qcolor)
                
    def setPosition(self):
        if self.hwro is not None and self.__lastPosition is not None:
            if self.hwro.mode.lower() == "absolute":
                allpos = {}
                for role,mot in self.hwro["motors"]._objectsByRole.items():
                    allpos[role] = mot.getPosition()
                self.hwro.setNewPositions(self.__lastPosition, allpos)
            else:
                for role,mot in self.hwro["motors"]._objectsByRole.items():
                    motpos = mot.getPosition()
                    savedpos = self.hwro.positions[self.__lastPosition][role]
                    offset = mot.getOffset()
                    newoffset = offset + savedpos - motpos
                    mot.setOffset(newoffset)
        
    def gotoPosition(self):
        if self.hwro is not None:
            self.hwro.moveToPosition(str(self.positionList.currentText()))
        
    def addPosition(self):
        if self.hwro is not None:
            pos = {}
            for role,mot in self.hwro["motors"]._objectsByRole.items():
                pos[role] = str(mot.getPosition())
                
            label_str = "Enter a name for position "
            key_str = "("
            pos_str = "("
            for key,val in pos.items():
                key_str = key_str + key
                pos_str = pos_str + val
            key_str = key_str+")"
            pos_str = pos_str+")"
            label_str = label_str+"%s:%s"%(key_str,pos_str)
            qrep = qt.QInputDialog.getText("New Position", label_str,
                                           qt.QLineEdit.Normal, "", None)
                                       
            if qrep[1]:
                rep = str(qrep[0])
                if rep != "":
                    pos["name"] = rep
                    self.hwro.addPosition(pos)
   
    def remPosition(self):
        if self.hwro is not None:
            self.hwro.remPosition(str(self.positionList.currentText()))
        
class MultiplePositionConfigurator(qt.QDialog):
    def __init__(self, parent):
        qt.QDialog.__init__(self, parent, "MultposConfigurator", False)
        
        """
        variables
        """
        self.motorIndexList = {}
        self.motorBrickList = {}
        self.motorConnList = []
        self.motorList = []
        self.hwro = None
        self.selPos = None
        
        """
        interface
        """     
        hlayout = qt.QHBoxLayout(self)
        hlayout.setMargin(5)
        hlayout.setSpacing(5)
                
        """
        value change window
        """
        self.frame = qt.QFrame(self)
        self.frame.setFrameShape(qt.QFrame.NoFrame)
        self.frame.setFrameShadow(qt.QFrame.Plain)
        hlayout.addWidget(self.frame)

        vlayout3 = qt.QVBoxLayout(self.frame)
        vlayout3.setMargin(5)
        """
        general set button
        """
        self.geneSetButton = qt.QPushButton("Store Current Motors Positions",
                                            self.frame)
        self.connect(self.geneSetButton, qt.SIGNAL("clicked()"),
                     self.__geneSet)
        vlayout3.addWidget(self.geneSetButton)
        
        """
        MotorSpinBoxBricks for all motors
        """
        vlayout3.addSpacing(20)
        vlayout3.setSpacing(5)
        
        self.motorLayout = qt.QVBoxLayout(vlayout3)
        
    def show(self):
        if self.hwro is not None:
            self.selPos = self.hwro.getPosition()
            if self.selPos is None:
                self.selPos = self.hwro.positionsIndex[0] 
        else:
            self.selPos = None          
        
        self.__setPosition()
                
        qt.QDialog.show(self)

    def __setPosition(self):
        if self.selPos is not None and self.hwro is not None:
            self.geneSetButton.setEnabled(True)
            if self.hwro.mode.lower() == "absolute":
                txt = "Store Current Motor Position for \"%s\""%self.selPos
            else:
                txt = "Set Stored Value as Motor Position for \"%s\""%self.selPos
            self.geneSetButton.setText(txt)
        else:
            self.geneSetButton.setEnabled(False)
        
    def setHardwareObject(self, hwro):
        self.hwro = hwro

        """
        general set button
        """
        if self.selPos is not None and self.hwro is not None:
            self.geneSetButton.setEnabled(True)
            if self.hwro.mode.lower() == "absolute":
                txt = "Store Current Motor Position for \"%s\""%self.selPos
            else:
                txt = "Set Stored Value as Motor Position for \"%s\""%self.selPos
            self.geneSetButton.setText(txt)
        else:
            self.geneSetButton.setEnabled(False)

        if self.hwro is not None:
            for role,mot in self.hwro["motors"]._objectsByRole.items():
                mne = role
                self.motorBrickList[mne] = MultiAxisAlignmentBrick(self.frame,"configure")
                self.motorBrickList[mne]["mnemonic"]=mot.name()
                self.motorBrickList[mne]["init percent size"]=0.0
                xml_gui_step = ""
                try:
                  xml_gui_step = (str(mot.getProperty("GUIstep"))+" ") or ""
                except:
                  pass
                self.motorBrickList[mne]["hori. steps"]=xml_gui_step + "0.05 0.1 0.5 1"
                self.motorBrickList[mne]["formatString"]="###.####"
                self.motorBrickList[mne].show()
                self.motorLayout.addWidget(self.motorBrickList[mne])
        
    def clearConfigurator(self):
        """
        index
        """
        self.motorIndexList = {}
        
        """
        Motor Bricks
        """
        for mne,brick in self.motorBrickList.items():
            brick.close(True)
        self.motorBrickList = {}

        """
        position
        """
        for conn in self.motorConnList:
            self.disconnect(conn, qt.PYSIGNAL("valueChanged"),
                            self.__motorPosChanged)
        self.motorConnList = []
      
    def __geneSet(self):
        if self.hwro is not None:
            if self.hwro.mode.lower() == "absolute":
                allpos = {}
                for role,mot in self.hwro["motors"]._objectsByRole.items():
                    allpos[role] = mot.getPosition()
                self.hwro.setNewPositions(self.selPos, allpos)
            else:
                for role,mot in self.hwro["motors"]._objectsByRole.items():
                    motpos = mot.getPosition()
                    savedpos = self.hwro.positions[self.selPos][role]
                    offset = mot.getOffset()
                    newoffset = offset + savedpos - motpos
                    mot.setOffset(newoffset)
            qt.QMessageBox.information(self, "Position alignment", "New position saved successfully.", qt.QMessageBox.Ok)
                
class QubRadioGroup(qt.QFrame):
    (Vertical, Horizontal) = (0,1)
    
    def __init__(self, orientation=Vertical, *args):
        qt.QFrame.__init__(self, *args)

        self.setFrameShape(qt.QFrame.NoFrame)
        self.setFrameShadow(qt.QFrame.Plain)
        
        if orientation == QubRadioGroup.Horizontal:
            self.layout = qt.QHBoxLayout(self)
        else:
            self.layout = qt.QVBoxLayout(self)
        self.layout.setMargin(5)
        self.layout.setSpacing(20)
        
        self.buttonList = {}
        
        self.__selectedRadio = None
        
    def addRadio(self, name):
        if name not in list(self.buttonList.keys()):
            self.buttonList[name] = QubRadioButton(str(name), self)
            self.layout.addWidget(self.buttonList[name])
            self.buttonList[name].show()
        
            self.connect(self.buttonList[name], qt.PYSIGNAL("PositionClicked"),
                         self.__positionClicked) 

    def isChecked(self, name):
        if name in list(self.buttonList.keys()):
            return self.buttonList[name].isChecked()
            
        return False
        
    def checked(self):
        return self.__selectedRadio
        
    def setChecked(self, name, value):
        if name in list(self.buttonList.keys()):
            if value:
                if self.__selectedRadio is not None:
                    self.buttonList[self.__selectedRadio].setChecked(False)
                self.__selectedRadio = name
            else:
                if self.__selectedRadio == name:
                    self.__selectedRadio = None

            self.buttonList[name].setChecked(value)

    def deselectAll(self):
        for name in list(self.buttonList.keys()):
            self.buttonList[name].setChecked(False)
         
    def setSpacing(self, val):
        self.layout.setSpacing(val)

    def clearRadioList(self):
        for name, radio in self.buttonList.items():
            self.disconnect(radio, qt.PYSIGNAL("PositionClicked"),
                            self.__positionClicked) 
            radio.close()
            
        self.buttonList = {}
        self.__selectedRadio = None
                
    def setMargin(self, val):
        self.layout.setMargin(val)
        
    def __positionClicked(self, name):
        self.setChecked(name, True)
        self.emit(qt.PYSIGNAL("PositionClicked"), (name,))
                        
class QubRadioButton(qt.QRadioButton):
    def __init__(self, *args):
        qt.QRadioButton.__init__(self, *args)
        
        self.connect(self, qt.SIGNAL("clicked()"), self.__positionClicked)
        
    def __positionClicked(self):
        name = str(self.text())
        self.emit(qt.PYSIGNAL("PositionClicked"), (name,))
        

class MotorConnection(qt.QWidget):
    def __init__(self, motorObject, ind,role):
        qt.QWidget.__init__(self, None)
        
        self.motor = motorObject
        self.index = ind
        self.__name = role
        
        self.motor.connect(self.motor, qt.PYSIGNAL("positionChanged"),
                           self.positionChanged) 
        self.motor.connect(self.motor, qt.PYSIGNAL("stateChanged"),
                           self.stateChanged) 
        
    def name(self):
        return self.__name
        
    def positionChanged(self, value):
        self.emit(qt.PYSIGNAL("ValueChanged"),
                  (value, self.__name, self.index))
    
    def stateChanged(self, state):
        self.emit(qt.PYSIGNAL("StateChanged"),
                  (state, self.__name, self.index))
                  
class QubLabel(qt.QLabel):
    def __init__(self, *args):
        qt.QLabel.__init__(self, *args)
        self.popupMenu = None
        
    def setPopup(self, popup):
        self.popupMenu = popup
        
    def mousePressEvent(self, MouseEvent) :
        if self.popupMenu is not None:
            if MouseEvent.button() == qt.Qt.RightButton:
                self.popupMenu.popup(self.mapToGlobal(MouseEvent.pos()))

class QubValue(qt.QWidget):

    (Horizontal, Vertical) = (0, 1)
    (Combo, Text, Label) = (0, 1, 2)
    
    def __init__(self, parent, \
                 titleType=Label, valueType=Label, orientation=Horizontal):
        qt.QWidget.__init__(self, parent)
        
        self.__valueList = []
        self.__titleList = []
        
        self.orientation = orientation
        self.titleType = titleType
        self.valueType = valueType
        
        if self.orientation == QubValue.Horizontal:
            self.layout = qt.QHBoxLayout(self)
        else:
            self.layout = qt.QVBoxLayout(self)
        
        if self.titleType == QubValue.Combo:
            self.titleWidget = qt.QComboBox(self)
            self.connect(self.titleWidget, qt.SIGNAL("activated(int)"),
                         self.__activatedType)
        else:   
            self.titleWidget = qt.QLabel(self)
        self.layout.addWidget(self.titleWidget)
        
        self.layout.addSpacing(5)
        
        if self.valueType == QubValue.Combo:
            self.valueWidget = qt.QComboBox(self)
            self.connect(self.valueWidget, qt.SIGNAL("activated(int)"),
                         self.__activatedValue)
        elif self.valueType == QubValue.Text:
            self.valueWidget = qt.QLineEdit(self)
            self.connect(self.valueWidget, qt.SIGNAL("returnPressed()"),
                         self.__returnPressed)
        else:
            self.valueWidget = qt.QLabel(self)            
            self.valueWidget.setFrameShape(qt.QFrame.NoFrame)
            self.valueWidget.setFrameShadow(qt.QFrame.Plain)
        self.layout.addWidget(self.valueWidget)
            
    def __returnPressed(self):
        self.emit(qt.PYSIGNAL("NewValue"),(self.valueWidget.text(), 0))
            
    def __activatedValue(self):
        ind = self.valueWidget.currentItem()
        text = self.valueWidget.currentText()
        self.emit(qt.PYSIGNAL("NewValue"),(text, ind))
            
    def __activatedTitle(self):
        ind = self.titleWidget.currentItem()
        text = self.titleWidget.currentText()
        self.emit(qt.PYSIGNAL("NewTitle"),(text, ind))
    
    def setComboValue(self, values):
        self.__valueList = values
        if self.valueType == QubValue.Combo:
            for value in values:
                self.valueWidget.insertItem(value)
    
    def setComboTitle(self, titles):
        self.__titleList = titles
        if self.titleType == QubValue.Combo:
            for title in titles:
                self.valueWidget.insertItem(titles)

    def setValueIndex(self, ind):
        if self.valueType == QubValue.Combo:
            self.valueWidget.setCurrentItem(ind)
                          
    def setValue(self, text):
        if self.valueType == QubValue.Combo:
            self.valueWidget.setCurrentItem(self.__valueList.index(text))
        else:
            self.valueWidget.setText(text)
        
    def setTitleIndex(self, ind):
        if self.titleType == QubValue.Combo:
            self.titleWidget.setCurrentItem(ind)
            
    def setTitle(self, text):
        if self.titleType == QubValue.Combo:
            self.titleWidget.setCurrentItem(self.__titleList.index(text))
        else:
            self.titleWidget.setText(text)
        
    def setValueMaximumSize(self, size):
        self.valueWidget.setMaximumSize(size)
        
    def setTitleMaximumSize(self, size):
        self.titleWidget.setMaximumSize(size)
        
    def setValueMinimumSize(self, size):
        self.valueWidget.setMinimumSize(size)
        
    def setTitleMinimumSize(self, size):
        self.titleWidget.setMinimumSize(size)
        
    def value(self):
        if self.valueType == QubValue.Combo:
            return self.valueWidget.currentText()
        else:
            return self.valueWidget.text()

    def valueIndex(self):
        if self.valueType == QubValue.Combo:
            return self.valueWidget.currentItem()
        else:
            return 0
        
    def title(self):
        if self.titleType == QubValue.Combo:
            return self.titleWidget.currentText()
        else:
            return self.titleWidget.text()

    def titleIndex(self):
        if self.titleType == QubValue.Combo:
            return self.titleWidget.currentItem()
        else:
            return 0
                    
    def valueSizeHint(self):
        return self.valueWidget.sizeHint()
        
    def titleSizeHint(self):
        return self.titleWidget.sizeHint()

    def valueBackgroundColor(self):
        return self.valueWidget.paletteBackgroungColor()
    
    def setValueBackgroundColor(self, color):
        self.valueWidget.setPaletteBackgroundColor(color)
        
