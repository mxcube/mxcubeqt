"""
[Name] AttenuatorsBrick

[Description]

The Attenuators brick allows user to read and set the transmission,
thus moving attenuators. 

Filters can be moved individually for expert
control or if transmission calculation is not available.

[Properties]

-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| mnemonic     | string | name of the Attenuators Hardware Object
| icons        | string | <apply button icon> <filters button icon>
| formatString | string | format string for transmission display (defaults to ###.##)
|  filtersMode  | combo  | Expert: Filters button is shown in Expert mode only, Enabled/Disabled: Filters button is always/never shown
-----------------------------------------------------------------------

[Signals]

[Slots]

-------------------------------------------------------------------
| name                | arguments                  | description
-------------------------------------------------------------------
| setEnabled          |                            | enables the brick
| transmissionRequest | transmission (dict) | used to set the transmission from another brick
-------------------------------------------------------------------
[Comments]

[HardwareObjects]

Known compatible hardware objects are:
- :hw:Attenuators

Compatible Hardware Objects should implements the following
methods :

- isReady()
- getAttFactor()
- getAttState()
- toggle(filter_index)
- setTransmission(transmission_percent)

Compatible Hardware Objects should also emit these signals :
- deviceReady
- deviceNotReady
- attStateChanged
- attFactorChanged

Example Hardware Object XML file :
==================================

<device class = "Attenuators">
  <username>Attenuators</username>
  <specversion>lid232:eh1</specversion>
  <command type="spec" name="toggle">attio</command>
  <command type="spec" name="setTransmission">transmission</command>
  <channel type="spec" name="attstate">MATT_STATE</channel>
  <channel type="spec" name="attfactor">ATT_FACTOR</channel>
  <atte>
     <label>PyroC 0.1</label>
     <bits>2048</bits>
  </atte>
  <atte>
     <label>PyroC 0.2</label>
     <bits>1024</bits>
  </atte>
  <atte>
     <label>PyroC 0.5</label>
     <bits>512</bits>
  </atte>
  <atte>
     <label>PyroC 0.8</label>
     <bits>256</bits>
  </atte>
  ...
  <atte>
     <label>Alum 4</label>
     <bits>1</bits>
  </atte>
</device>

"""
import logging
from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar
from BlissFramework.Utils import widget_colors


class AtteFilter(QCheckBox):
    def __init__(self,label,parent,idx):
        QCheckBox.__init__(self,str(label),parent)
	self.idx=idx
        self.connect(self,SIGNAL("toggled(bool)"),self.toggleme)

    def toggleme(self):
        self.emit(PYSIGNAL("toggleFilter"),(self.idx,))

    def checkme(self,stat):
        self.blockSignals(True)
        self.setChecked(stat)
        self.blockSignals(False)

class AttenuatorsBrick(BlissWidget):
    CONNECTED_COLOR = widget_colors.LIGHT_GREEN
    CHANGED_COLOR = QColor(255,165,0)
    OUTLIMITS_COLOR = widget_colors.LIGHT_RED

    MAX_HISTORY = 20

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty('mnemonic', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('formatString','formatString','###.##')
        self.addProperty('filtersMode', 'combo',('Expert','Enabled','Disabled'),'Expert')

        self.defineSlot('setEnabled',())
        self.defineSlot('transmissionRequest',())

        self.attenuators = None
        self.transmissionLimits=None

        self.currentTransmissionValue=None

        self.filtersDialog=FiltersDialog(self)

        self.topBox = QHGroupBox('Transmission', self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)

        self.paramsBox = QWidget(self.topBox)
        QGridLayout(self.paramsBox, 2, 3, 0, 2)

        label1=QLabel("Current:",self.paramsBox)
        self.paramsBox.layout().addWidget(label1, 0, 0)

        self.currentTransmission=QLineEdit(self.paramsBox)
        self.currentTransmission.setReadOnly(True)
        self.currentTransmission.setFixedWidth(75)
        #f=self.currentTransmission.font()
        #f.setBold(True)
        #self.currentTransmission.setFont(f)
        self.paramsBox.layout().addWidget(self.currentTransmission, 0, 1)

        label2=QLabel("Set to:",self.paramsBox)
        self.paramsBox.layout().addWidget(label2, 1, 0)

        #box1=QHBox(self.paramsBox)
        self.newTransmission=QLineEdit(self.paramsBox)
        self.newTransmission.setAlignment(QWidget.AlignRight)
        self.paramsBox.layout().addWidget(self.newTransmission, 1, 1)
        #pol=self.newTransmission.sizePolicy()
        #pol.setVerData(QSizePolicy.MinimumExpanding)
        #self.newTransmission.setSizePolicy(pol)
        self.newTransmission.setFixedWidth(75)
        #self.applyButton=QPushButton("+",box1)
        #QObject.connect(self.applyButton,SIGNAL('clicked()'),self.changeCurrentTransmission)
        #self.paramsBox.layout().addWidget(box1, 1, 1)
        self.newTransmission.setValidator(QDoubleValidator(self))
        self.newTransmission.setPaletteBackgroundColor(AttenuatorsBrick.CONNECTED_COLOR)
        QObject.connect(self.newTransmission, SIGNAL('returnPressed()'),self.changeCurrentTransmission)
        QObject.connect(self.newTransmission, SIGNAL('textChanged(const QString &)'),self.inputFieldChanged)
        self.newTransmission.createPopupMenu=self.openHistoryMenu

        self.instanceSynchronize("newTransmission")

        self.filtersButton=QToolButton(self.paramsBox)
        self.filtersButton.setTextLabel("Filters")
        self.filtersButton.setUsesTextLabel(True)        
        self.paramsBox.layout().addMultiCellWidget(self.filtersButton, 0, 1, 2, 2)
        QObject.connect(self.filtersButton,SIGNAL('clicked()'),self.openFiltersDialog)

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            if self.attenuators is not None:
                self.disconnect(self.attenuators, PYSIGNAL('deviceReady'), self.connected)
                self.disconnect(self.attenuators, PYSIGNAL('deviceNotReady'), self.disconnected)
                self.disconnect(self.attenuators, PYSIGNAL('attStateChanged'), self.attStateChanged)
                self.disconnect(self.attenuators, PYSIGNAL('attFactorChanged'), self.attFactorChanged)

            self.transHistory=[]
 
            self.attenuators = self.getHardwareObject(newValue)
            if self.attenuators is not None:
                self.filtersDialog.setAttenuators(self.attenuators)

                self.connect(self.attenuators, PYSIGNAL('deviceReady'), self.connected)
                self.connect(self.attenuators, PYSIGNAL('deviceNotReady'), self.disconnected)
                self.connect(self.attenuators, PYSIGNAL('attStateChanged'), self.attStateChanged)
                self.connect(self.attenuators, PYSIGNAL('attFactorChanged'), self.attFactorChanged)
                if self.attenuators.isReady():
                    self.connected()
                    self.attFactorChanged(self.attenuators.getAttFactor())
                    self.attStateChanged(self.attenuators.getAttState())
                else:
                    self.disconnected()
            else:
                self.disconnected()

        elif property == 'filtersMode':
            if newValue == 'Disabled':
                self.filtersButton.hide()

        elif property == 'icons':
            icons_list=newValue.split()

            #try:
            #    self.applyButton.setPixmap(Icons.load(icons_list[0]))
            #except IndexError:
            #    pass

            try:
                self.filtersButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass
        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)

    def inputFieldChanged(self,text):
        text=str(text)
        if text=="":
            self.newTransmission.setPaletteBackgroundColor(AttenuatorsBrick.CONNECTED_COLOR)
        else:
            try:
                val=float(text)
            except (TypeError,ValueError):
                widget_color=AttenuatorsBrick.OUTLIMITS_COLOR
            else:
                widget_color=AttenuatorsBrick.CHANGED_COLOR
                if self.transmissionLimits is not None:
                    if val<self.transmissionLimits[0] or val>self.transmissionLimits[1]:
                        widget_color=AttenuatorsBrick.OUTLIMITS_COLOR

            self.newTransmission.setPaletteBackgroundColor(widget_color)

    def transmissionRequest(self,param_dict):
        try:
            val=float(str(self.newTransmission.text()))
        except (ValueError,TypeError):
            pass
        else:
            if self.transmissionLimits is not None:
                if val>=self.transmissionLimits[0] and val<=self.transmissionLimits[1]:
                    param_dict['transmission']=val
            else:
                param_dict['transmission']=val

        try:
            curr_transmission=float(self.currentTransmissionValue)
        except (ValueError,TypeError,IndexError):
            pass
        else:
            param_dict['current_transmission']=curr_transmission

    def changeCurrentTransmission(self):
        try:
            val=float(str(self.newTransmission.text()))
        except (ValueError,TypeError):
            return

        if self.transmissionLimits is not None:
            if val<self.transmissionLimits[0] or val>self.transmissionLimits[1]:
                return

        self.attenuators.setTransmission(val)
        #self.newTransmission.blockSignals(True)
        self.newTransmission.setText('')
        #self.newTransmission.blockSignals(False)

    def connected(self):
        self.transmissionLimits=(0,100)
        #self.currentTransmission.setDisabledLook(False)
        self.topBox.setEnabled(True)

    def disconnected(self):
        self.transmissionLimits=None
        self.filtersDialog.accept()
        #self.currentTransmission.setDisabledLook(True)
        self.topBox.setEnabled(False)

    def setExpertMode(self,state):
        #print "enableFilters",state
        if self['filtersMode']=='Expert':
            self.filtersButton.setEnabled(state)
            if not state:
                self.filtersDialog.accept()

    def attStateChanged(self, value):
        #print "Attenuators.attStateChanged",value
        if value is None:
            return
        self.filtersDialog.filtersChanged(value)

    def attFactorChanged(self, value):
        #print "Attenuators.attFactorChanged",value,self
        self.currentTransmissionValue=value
        if value is None:
            return
        if value < 0:
            self.currentTransmissionValue=None
            self.currentTransmission.setText("")
            #self.currentTransmission.setDisabledLook(True)
        else:
            att_str=self['formatString'] % value
            self.currentTransmissionValue=att_str
            self.currentTransmission.setText('%s%%' % att_str)
            #self.currentTransmission.setDisabledLook(False)
            self.updateTransHistory(att_str)

    def updateTransHistory(self,trans):
        if trans not in self.transHistory:
            if len(self.transHistory)==AttenuatorsBrick.MAX_HISTORY:
                del self.transHistory[-1]
            self.transHistory.insert(0,trans)
        #self.newTransmission.createPopupMenu=self.openHistoryMenu

    def openHistoryMenu(self):
        menu=QPopupMenu(self)
        menu.insertItem(QLabel('<nobr><b>Transmission history</b></nobr>', menu))
        menu.insertSeparator()
        for i in range(len(self.transHistory)):
            menu.insertItem("%s%%" % self.transHistory[i],i)
        QObject.connect(menu,SIGNAL('activated(int)'),self.goToTransHistory)
        return menu

    def goToTransHistory(self,idx):
        trans=float(self.transHistory[idx])
        self.attenuators.setTransmission(trans)

    def openFiltersDialog(self):
        s=self.font().pointSize()
        f=self.filtersDialog.font()
        f.setPointSize(s)
        self.filtersDialog.setFont(f)
        self.filtersDialog.updateGeometry()
        self.filtersDialog.show()
        self.filtersDialog.setActiveWindow()
        self.filtersDialog.raiseW()

    def instanceModeChanged(self,mode):
        if mode==BlissWidget.INSTANCE_MODE_SLAVE:
            self.filtersDialog.reject()

class FiltersDialog(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent,'',False)
        self.attenuators=None
        self.setCaption('Transmission')
        self.contentsBox=QVGroupBox('Filters',self)
        self.contentsBox.setInsideMargin(4)
        self.contentsBox.setInsideSpacing(2)
        buttonsBox=DialogButtonsBar(self,"Dismiss",None,None,self.buttonClicked,0,DialogButtonsBar.DEFAULT_SPACING)
        QVBoxLayout(self,6,6)
        self.layout().addWidget(self.contentsBox)
        self.layout().addWidget(buttonsBox)

        self.attlist=[]
        self.n_atte=0

    def setAttenuators(self,att):
        for attitem in self.attlist:
            self.disconnect(attitem,PYSIGNAL("toggleFilter"),self.toggleFilter)
            attitem.close(True)
        self.attlist=[]

        self.attenuators=att
        att.getAtteConfig()
        self.n_atte=self.attenuators.attno
        for filt in range(self.n_atte):
            label=self.attenuators.labels[filt]
            filt=AtteFilter(label,self.contentsBox,filt)
            self.connect(filt,PYSIGNAL("toggleFilter"),self.toggleFilter)
            self.attlist.append(filt)

    def buttonClicked(self,action):
        self.accept()

    def toggleFilter(self,filter_id):
    	#print "dialog.toggleFilter",filter_id
        self.attenuators.toggle(filter_id)

    def filtersChanged(self,value):
        try:
           for idx in range(self.n_atte):
               self.attlist[idx].checkme(self.attenuators.is_in(idx))
        except ValueError:
           logging.getLogger().warning('AttenuatorsBrick: error reading filter status (%d)' % value)


class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
