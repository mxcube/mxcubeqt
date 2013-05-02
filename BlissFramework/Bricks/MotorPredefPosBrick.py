from BlissFramework import BaseComponents
from BlissFramework.Bricks import MotorWPredefinedPositionsBrick
from qt import *
from BlissFramework.Utils import widget_colors

'''
'''

__category__ = 'Motor'

class MotorPredefPosBrick(MotorWPredefinedPositionsBrick.MotorWPredefinedPositionsBrick):

    STATE_COLORS = (widget_colors.LIGHT_RED, widget_colors.LIGHT_RED,\
        widget_colors.LIGHT_GREEN,\
        QWidget.yellow, QWidget.yellow,\
        QWidget.darkYellow)

    #DISABLED_COLOR = None

    def __init__(self, *args):
        MotorWPredefinedPositionsBrick.MotorWPredefinedPositionsBrick.__init__(self, *args)

        self.addProperty('label','string','')
        self.addProperty('listIndex','integer', -1)

        self.lblUsername.close()
        self.expertPanel.close()
        self.posButtonsPanel.close()

        self.positions=None

        box1=QHBox(self)
        self.label2=QLabel("motor:",box1)
        self.layout().addWidget(box1, 0)
        self.lstPositions.reparent(box1,0,QPoint(0,0),True)
        box1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.label2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)

        QToolTip.add(self.lstPositions,"Moves the motor to a predefined position")

        self.defineSlot('setEnabled',())

    def setToolTip(self,name=None,state=None):
        states=("NOTREADY","UNUSABLE","READY","MOVESTARTED","MOVING","ONLIMIT")
        if name is None:
            name=self['mnemonic']

        if self.motor is None:
            tip="Status: unknown motor "+name
        else:
            if state is None:
                state=self.motor.getState()
            try:
                state_str=states[state]
            except IndexError:
                state_str="UNKNOWN"
            tip="State:"+state_str

        QToolTip.add(self.label2,tip)

    def motorStateChanged(self, state):
        """
        if MotorPredefPosBrick.DISABLED_COLOR is None:
            combobox_palette=self.lstPositions.palette()
            disabled_group=QColorGroup(combobox_palette.disabled())
            MotorPredefPosBrick.DISABLED_COLOR=self.colorGroup().background()
        """

        MotorWPredefinedPositionsBrick.MotorWPredefinedPositionsBrick.motorStateChanged(self,state)
        color=MotorPredefPosBrick.STATE_COLORS[state]
        self.lstPositions.setPaletteBackgroundColor(color)

        """
        combobox_palette=self.lstPositions.palette()
        disabled_group=QColorGroup(combobox_palette.disabled())
        disabled_group.setColor(disabled_group.Background,\
            self.colorGroup().background())
        combobox_palette.setDisabled(disabled_group)
        """

        self.setToolTip(state=state)

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=='label':
            if newValue=="" and self.motor is not None:
                self.label2.setText("<i>"+self.motor.username+":</i>")
                tip=self.motor.username
            else:
                self.label2.setText(newValue)
                tip=newValue
        elif propertyName=='mnemonic':
            MotorWPredefinedPositionsBrick.MotorWPredefinedPositionsBrick.propertyChanged(self,propertyName,oldValue,newValue)
            if self.motor is not None and self['label']=="":
                lbl=self.motor.username
                self.label2.setText("<i>"+lbl+":</i>")
            if self.motor is None:
                self.lstPositions.setPaletteBackgroundColor(MotorPredefPosBrick.STATE_COLORS[0])
            else:
                self.motorStateChanged(self.motor.getState())
        elif propertyName=='listIndex':
            self.fillPositions()
        else:
            MotorWPredefinedPositionsBrick.MotorWPredefinedPositionsBrick.propertyChanged(self,propertyName,oldValue,newValue)

    def setMnemonic(self,mne):
        MotorWPredefinedPositionsBrick.MotorWPredefinedPositionsBrick.setMnemonic(self,mne)
        self.lblUsername.setText('')
        self.setToolTip(name=mne)

    def fillPositions(self, positions = None): 
        self.cleanPositions()

        if self.motor is not None:
            if positions is None:
                positions = self.motor.getPredefinedPositionsList()

        if positions is None:
            positions=[]

        list_index=self['listIndex']	  
        for p in positions:
            if list_index!=-1:
                pos_list=p.split()
                pos_name=pos_list[list_index]
            else:
                pos_name=p
            self.lstPositions.insertItem(str(pos_name))

            if self['showButtons']:
                b = QPushButton(p, self.posButtonsPanel)
                b.setToggleButton(True)
                QObject.connect(b, SIGNAL('clicked()'), self.posButtonClicked) 
                self.buttons.append(b)                                           
                b.show()

        self.positions=positions

        if self.motor is not None:
            if self.motor.isReady():
                self.predefinedPositionChanged(self.motor.getCurrentPositionName(), 0)
          
        if self['showButtons']:
            self.lstPositions.hide()
            self.posButtonsPanel.show()
        else:
            self.lstPositions.show()
            self.posButtonsPanel.hide()	      

    def lstPositionsClicked(self, index):
        if index > 0:
            if self.motor.isReady():
                self.motor.moveToPosition(self.positions[index-1])
            else:
                self.lstPositions.setCurrentItem(0)

    def predefinedPositionChanged(self, positionName, offset):
        self.lstPositions.setCurrentItem(0)

        for button in self.buttons:
            button.show()
            button.setOn(False)
            
        for i in range(len(self.positions)):
            if self.positions[i] == positionName:
                self.lstPositions.setCurrentItem(i+1)
            if len(self.buttons) > 0:
                self.buttons[i].setOn(True)
                break
