import logging

from qt import *
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Utils import widget_colors


__category__ = 'mxCuBE'

class ResolutionBrick(BlissWidget):
    STATE_COLORS = (widget_colors.LIGHT_RED, 
                    widget_colors.LIGHT_RED,
                    widget_colors.LIGHT_GREEN,
                    widget_colors.LIGHT_YELLOW, 
                    widget_colors.LIGHT_YELLOW,
                    QWidget.darkYellow,
                    QColor(255,165,0),
                    widget_colors.LIGHT_RED)

    MAX_HISTORY = 20

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.resolutionMotor=None
        self.detectorMotor=None
        self.energyHObj=None
        self.colorGroupDict={}
        self.originalBackgroundColor=None

        self.resolutionLimits=None
        self.detectorLimits=None

        self.resolutionThread=None

        self.currentResolutionValue=None
        self.currentDetDistanceValue=None

        self.addProperty('resolution', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('defaultMode', 'combo',('Ang','mm'),'Ang')
        self.addProperty('mmFormatString','formatString','###.##')
        self.addProperty('angFormatString','formatString','##.###')

        self.defineSlot('setEnabled',())
        self.defineSlot('resolutionRequest',())

        self.topBox = QVGroupBox("Resolution",self)
        self.topBox.setInsideMargin(4)
        self.topBox.setInsideSpacing(2)

        self.paramsBox = QWidget(self.topBox)
        QGridLayout(self.paramsBox, 2, 5, 0, 2)

        label1=QLabel("Current:",self.paramsBox)
        self.paramsBox.layout().addWidget(label1, 0, 0)

        box1=QVBox(self.paramsBox)
        self.currentResolution=QLineEdit(box1)
        self.currentResolution.setReadOnly(True)
        self.currentDetectorDistance=QLineEdit(box1)
        self.currentDetectorDistance.setReadOnly(True)
        self.paramsBox.layout().addMultiCellWidget(box1, 0, 0, 1, 3)

        label2=QLabel("Move to:",self.paramsBox)
        self.paramsBox.layout().addWidget(label2, 1, 0)

        self.newValue=QLineEdit(self.paramsBox)
        self.paramsBox.layout().addWidget(self.newValue, 1, 1)
        self.newValue.setValidator(QDoubleValidator(self))
        self.newValue.setAlignment(QWidget.AlignRight)
        self.newValue.setFixedWidth(50)
        pol=self.newValue.sizePolicy()
        pol.setVerData(QSizePolicy.MinimumExpanding)
        self.newValue.setSizePolicy(pol)
        QObject.connect(self.newValue, SIGNAL('returnPressed()'),self.changeCurrentValue)
        QObject.connect(self.newValue, SIGNAL('textChanged(const QString &)'), self.inputFieldChanged)
        self.newValue.createPopupMenu=self.openHistoryMenu
        self.units=QComboBox(self.paramsBox)
        self.units.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        self.paramsBox.layout().addWidget(self.units, 1, 2)
        QObject.connect(self.units,SIGNAL('activated(const QString &)'),self.unitChanged)

        self.instanceSynchronize("topBox","newValue","units")

        box2=QHBox(self.paramsBox)
        box2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        #self.applyButton=QPushButton("+",box2)
        #QObject.connect(self.applyButton,SIGNAL('clicked()'),self.changeCurrentValue)
        self.stopButton=QPushButton("*",box2)
        self.stopButton.setEnabled(False)
        QObject.connect(self.stopButton,SIGNAL('clicked()'),self.stopClicked)
        self.paramsBox.layout().addWidget(box2, 1, 3)

        #self.applyButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)
        self.stopButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.MinimumExpanding)

        QVBoxLayout(self)
        self.layout().addWidget(self.topBox)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)

    def propertyChanged(self, property, oldValue, newValue):
        if property == 'resolution':
            if self.resolutionMotor is not None:
                self.disconnect(self.resolutionMotor,PYSIGNAL('deviceReady'),self.resolutionReady)
                self.disconnect(self.resolutionMotor,PYSIGNAL('deviceNotReady'),self.resolutionNotReady)
                self.disconnect(self.resolutionMotor,PYSIGNAL('stateChanged'),self.resolutionStateChanged)
                self.disconnect(self.resolutionMotor,PYSIGNAL('positionChanged'),self.resolutionChanged)
            if self.detectorMotor is not None:
                self.disconnect(self.detectorMotor,PYSIGNAL('deviceReady'),self.resolutionReady)
                self.disconnect(self.detectorMotor,PYSIGNAL('deviceNotReady'),self.resolutionNotReady)
                self.disconnect(self.detectorMotor,PYSIGNAL('stateChanged'),self.detectorStateChanged)
                self.disconnect(self.detectorMotor,PYSIGNAL('positionChanged'),self.detectorChanged)
                self.disconnect(self.detectorMotor,PYSIGNAL('limitsChanged'),self.detectorLimitsChanged)
            if self.energyHObj is not None:
                self.disconnect(self.energyHObj,PYSIGNAL('moveEnergyFinished'),self.energyChanged)
            self.units.clear()
            self.angHistory=[]
            self.mmHistory=[]
            available_units=[]
            self.resolutionMotor=self.getHardwareObject(newValue)
            self.detectorMotor = None
            self.energyHObj = None
            if self.resolutionMotor is not None:
                self.detectorMotor=self.resolutionMotor.dtox
                self.energyHObj = self.resolutionMotor.energy

                self.units.insertItem(chr(197))
                available_units.append('Ang')

                if self.detectorMotor is not None:
                    self.units.insertItem('mm')
                    available_units.append('mm')

                try:
                    self.connect(self.resolutionMotor,PYSIGNAL('deviceReady'),self.resolutionReady)
                    self.connect(self.resolutionMotor,PYSIGNAL('deviceNotReady'),self.resolutionNotReady)
                    self.connect(self.resolutionMotor,PYSIGNAL('stateChanged'),self.resolutionStateChanged)
                    self.connect(self.resolutionMotor,PYSIGNAL('positionChanged'),self.resolutionChanged)
                except:
                    logging.getLogger().exception('ResolutionBrick: problem connecting to the resolution motor')
                try:
                    self.connect(self.detectorMotor,PYSIGNAL('deviceReady'),self.resolutionReady)
                    self.connect(self.detectorMotor,PYSIGNAL('deviceNotReady'),self.resolutionNotReady)
                    self.connect(self.detectorMotor,PYSIGNAL('stateChanged'),self.detectorStateChanged)
                    self.connect(self.detectorMotor,PYSIGNAL('positionChanged'),self.detectorChanged)
                    self.connect(self.detectorMotor,PYSIGNAL('limitsChanged'),self.detectorLimitsChanged)
                except:
                    logging.getLogger().exception('ResolutionBrick: problem connecting to the detector distance motor')
                try:
                    self.connect(self.energyHObj,PYSIGNAL('moveEnergyFinished'),self.energyChanged)
                except:
                    logging.getLogger().exception('ResolutionBrick: problem connecting to the energy motor')
                if self.resolutionMotor.isReady():
                    self.resolutionReady()
                else:
                    self.resolutionNotReady()
            else:
                if self.detectorMotor is not None:
                    self.units.insertItem('mm')
                    available_units.append('mm')

                self.updateGUI()

            try:
                i=available_units.index(self['defaultMode'])
            except ValueError:
                #curr=str(self.units.currentText())
                curr=self.units.currentText()
                if curr!="":
                    self.unitChanged(curr)
            else:
                def_mode=self['defaultMode']
                if def_mode=='Ang':
                    def_mode=chr(197)
                self.units.setCurrentText(def_mode)
                self.unitChanged(def_mode)
        elif property == 'icons':
            icons_list=newValue.split()

            try:
                self.stopButton.setPixmap(Icons.load(icons_list[1]))
            except IndexError:
                pass

        else:
            BlissWidget.propertyChanged(self,property,oldValue,newValue)


    def detectorLimitsChanged(self,limits):
        self.detectorLimits=limits
        self.getResolutionLimits(True)


    def resolutionLimitsChanged(self,limits):
        if not None in limits:
            logging.getLogger().info("Resolution limits changed to (%3.3f, %3.3f)", *limits)
        self.resolutionLimits=limits
        #self.resolutionThread.wait()
        #self.resolutionThread=None


    def inputFieldChanged(self,text):
        text=str(text)
        if text=="":
            curr=self.units.currentText()
            if curr!="":
                self.unitChanged(curr)
        else:
            try:
                val=float(text)
            except (ValueError,TypeError):
                color_index=7
            else:
                unit=self.units.currentText()
                limits=None
                if unit==chr(197):
                    limits=self.resolutionLimits
                elif unit=="mm":
                    limits=self.detectorLimits

                if limits is not None:
                    if val>=limits[0] and val<=limits[1]:
                        color_index=6
                    else:
                        color_index=7
                else:
                    color_index=6

            color=ResolutionBrick.STATE_COLORS[color_index]
            self.newValue.setPaletteBackgroundColor(color)

    def resolutionRequest(self,param_dict):
        unit=self.units.currentText()
        try:
            val=float(str(self.newValue.text()))
        except (ValueError,TypeError):
            pass
        else:
            if unit==chr(197):
                if self.resolutionLimits is not None:
                    if val>=self.resolutionLimits[0] and val<=self.resolutionLimits[1]:
                        param_dict['resolution']=val
                else:
                    param_dict['resolution']=val
            elif unit=="mm":
                if self.detectorLimits is not None:
                    if val>=self.detectorLimits[0] and val<=self.detectorLimits[1]:
                        param_dict['detdistance']=val
                else:
                    param_dict['detdistance']=val

        try:
            curr_resolution=float(self.currentResolutionValue)
        except (ValueError,TypeError,IndexError):
            pass
        else:
            param_dict['current_resolution']=curr_resolution
        try:
            curr_detdistance=float(self.currentDetDistanceValue)
        except (ValueError,TypeError,IndexError):
            pass
        else:
            param_dict['current_detdistance']=curr_detdistance

    def unitChanged(self,unit):
        f_mm=self.currentDetectorDistance.font()
        f_ang=self.currentResolution.font()
        if unit==chr(197):
            #f_mm.setBold(False)
            #f_ang.setBold(True)
            self.topBox.setTitle('Resolution')
            self.resolutionStateChanged(self.resolutionMotor.getState())
        elif unit=="mm":
            #f_mm.setBold(True)
            #f_ang.setBold(False)
            self.topBox.setTitle('Detector distance')
            self.detectorStateChanged(self.detectorMotor.getState())
        self.currentDetectorDistance.setFont(f_mm)
        self.currentResolution.setFont(f_ang)
        self.newValue.blockSignals(True)
        self.newValue.setText("")
        self.newValue.blockSignals(False)

    def updateGUI(self,resolution_ready=None,detector_ready=None):
        #print "ResolutionBrick.updateGUI",resolution_ready,detector_ready

        if self.resolutionMotor is None:
            resolution_ready=False
        elif resolution_ready is None:
            try:
                if self.resolutionMotor.connection.isSpecConnected():
                    resolution_ready=self.resolutionMotor.isReady()
            except AttributeError:
                resolution_ready=self.resolutionMotor.isReady()

        if self.detectorMotor is None:
            detector_ready=False
        elif detector_ready is None:
            try:
                if self.detectorMotor.connection.isSpecConnected():
                    detector_ready=self.detectorMotor.isReady()
            except AttributeError:
                detector_ready=self.detectorMotor.isReady()

        if resolution_ready:
            self.getResolutionLimits(False,True)
            curr_resolution=self.resolutionMotor.getPosition()
            self.resolutionChanged(curr_resolution)
            self.setResolutionWidgetColor(self.resolutionMotor.getState())
        else:
            self.setResolutionWidgetColor()

        if detector_ready:
            self.getDetectorLimits()
            curr_detector=self.detectorMotor.getPosition()
            self.detectorChanged(curr_detector)
            self.setDetectorWidgetColor(self.detectorMotor.getState())
        else:
            self.setDetectorWidgetColor()

    def resolutionReady(self):
        self.updateGUI(resolution_ready=True)

    def resolutionNotReady(self):
        self.updateGUI(resolution_ready=False)

    def detectorReady(self):
        self.updateGUI(detector_ready=True)

    def detectorNotReady(self):
        self.updateGUI(detector_ready=False)

    def setResolution(self,ang):
        if self.resolutionLimits is not None:
            if ang<self.resolutionLimits[0] or ang>self.resolutionLimits[1]:
                return
        self.resolutionMotor.move(ang)

    def setDetectorDistance(self,mm):
        if self.detectorLimits is not None:
            if mm<self.detectorLimits[0] or mm>self.detectorLimits[1]:
                return
        self.detectorMotor.move(mm)

    def energyChanged(self):
        self.getResolutionLimits(True)

    def getResolutionLimits(self,force=False,resolution_ready=None):
        if self.resolutionLimits is not None and force is False:
            return
 
        if resolution_ready is None:
            resolution_ready=False
            if self.resolutionMotor is not None:
                try:
                    if self.resolutionMotor.connection.isSpecConnected():
                        resolution_ready=self.resolutionMotor.isReady()
                except AttributeError:
                    resolution_ready=self.resolutionMotor.isReady()
                    
        if resolution_ready:
            self.resolutionLimitsChanged(self.resolutionMotor.getLimits())
        else:
            self.resolutionLimits=None

    def getDetectorLimits(self,force=False):
        if self.detectorLimits is not None and force is False:
            return

        detector_ready=False
        if self.detectorMotor is not None:
            try:
                if self.detectorMotor.connection.isSpecConnected():
                    detector_ready=self.detectorMotor.isReady()
            except AttributeError:
                detector_ready=self.detectorMotor.isReady()
        if detector_ready:
            self.detectorLimits=self.detectorMotor.getLimits()
        else:
            self.detectorLimits=None

    def resolutionChanged(self,resolution):
        try:
          resolution_str=self['angFormatString'] % float(resolution)
        except:
          return
        self.currentResolutionValue=self['angFormatString'] % resolution
        self.currentResolution.setText("%s %s" % (resolution_str,chr(197)))

    def detectorChanged(self,detector):
        detector_str=self['mmFormatString'] % detector
        self.currentDetDistanceValue=self['mmFormatString'] % detector
        self.currentDetectorDistance.setText("%s mm" % detector_str)

    def changeCurrentValue(self):
        unit=self.units.currentText()
        try:
            val=float(str(self.newValue.text()))
        except (ValueError,TypeError):
            return
        if unit==chr(197):
            self.setResolution(val)
        elif unit=="mm":
            self.setDetectorDistance(val)

    def setResolutionWidgetColor(self,state=None):
        pass
        #if state is None:
        #    state=self.detectorMotor.NOTINITIALIZED

        #if state==self.detectorMotor.NOTINITIALIZED or state==self.detectorMotor.UNUSABLE:
        #    self.currentResolution.setDisabledLook(True)
        #else:
        #    self.currentResolution.setDisabledLook(False)

        self.resolutionStateChanged(state)

    def setDetectorWidgetColor(self,state=None):
        pass
        #if state is None:
        #    state=self.detectorMotor.NOTINITIALIZED

        #if state==self.detectorMotor.NOTINITIALIZED or state==self.detectorMotor.UNUSABLE:
        #    self.currentDetectorDistance.setDisabledLook(True)
        #else:
        #    self.currentDetectorDistance.setDisabledLook(False)

        #self.detectorStateChanged(state)

    def resolutionStateChanged(self,state):
        if self.detectorMotor is not None:
            if state==self.detectorMotor.MOVESTARTED:
                self.updateAngHistory(self.resolutionMotor.getPosition())

            if state:
                color=ResolutionBrick.STATE_COLORS[state]
            else:
                color = widget_colors.LIGHT_RED

            unit=self.units.currentText()
            if unit==chr(197):
                if state==self.detectorMotor.READY:
                    self.newValue.blockSignals(True)
                    self.newValue.setText("")
                    self.newValue.blockSignals(False)
                    self.newValue.setEnabled(True)
                else:
                    self.newValue.setEnabled(False)
                if state==self.detectorMotor.MOVING or state==self.detectorMotor.MOVESTARTED:
                    self.stopButton.setEnabled(True)
                else:
                    self.stopButton.setEnabled(False)

                self.newValue.setPaletteBackgroundColor(color)

                if state==self.detectorMotor.READY:
                    if self.originalBackgroundColor is None:
                        self.originalBackgroundColor=self.paletteBackgroundColor()
                    color=self.originalBackgroundColor

                w_palette=self.newValue.palette()
                try:
                    cg=self.colorGroupDict[state]
                except KeyError:
                    cg=QColorGroup(w_palette.disabled())
                    cg.setColor(cg.Background,color)
                    self.colorGroupDict[state]=cg
                w_palette.setDisabled(cg)

    def detectorStateChanged(self,state):
        if state==self.detectorMotor.MOVESTARTED:
            self.updateMmHistory(self.detectorMotor.getPosition())

        color=ResolutionBrick.STATE_COLORS[state]
        unit=self.units.currentText()
        if unit=="mm":
            if state==self.detectorMotor.READY:
                self.newValue.blockSignals(True)
                self.newValue.setText("")
                self.newValue.blockSignals(False)
                self.newValue.setEnabled(True)
            else:
                self.newValue.setEnabled(False)
            if state==self.detectorMotor.MOVING or state==self.detectorMotor.MOVESTARTED:
                self.stopButton.setEnabled(True)
            else:
                self.stopButton.setEnabled(False)

            self.newValue.setPaletteBackgroundColor(color)

            if state==self.detectorMotor.READY:
                if self.originalBackgroundColor is None:
                    self.originalBackgroundColor=self.paletteBackgroundColor()
                color=self.originalBackgroundColor

            w_palette=self.newValue.palette()
            try:
                cg=self.colorGroupDict[state]
            except KeyError:
                cg=QColorGroup(w_palette.disabled())
                cg.setColor(cg.Background,color)
                self.colorGroupDict[state]=cg
            w_palette.setDisabled(cg)    

    def stopClicked(self):
        unit=self.units.currentText()
        if unit==chr(197):
            self.resolutionMotor.stop()
        elif unit=="mm":
            self.detectorMotor.stop()

    def openHistoryMenu(self):
        unit=self.units.currentText()
        history=None
        if unit==chr(197):
            title='Resolution'
            history=self.angHistory
            sig=self.goToAngHistory
        elif unit=="mm":
            title='Detector distance'
            history=self.mmHistory
            sig=self.goToMmHistory

        if history is not None:
            menu=QPopupMenu(self)
            menu.insertItem(QLabel('<nobr><b>%s history</b></nobr>' % title, menu))
            menu.insertSeparator()
            for i in range(len(history)):
                menu.insertItem(history[i],i)
            QObject.connect(menu,SIGNAL('activated(int)'),sig)
            return menu

    def updateAngHistory(self,ang):
        ang=str(ang)
        if ang not in self.angHistory:
            if len(self.angHistory)==ResolutionBrick.MAX_HISTORY:
                del self.angHistory[-1]
            self.angHistory.insert(0,ang)

    def updateMmHistory(self,mm):
        mm=str(mm)
        if mm not in self.mmHistory:
            if len(self.mmHistory)==ResolutionBrick.MAX_HISTORY:
                del self.mmHistory[-1]
            self.mmHistory.insert(0,mm)

    def goToMmHistory(self,idx):
        mm=float(self.mmHistory[idx])
        self.setDetectorDistance(mm)

    def goToAngHistory(self,idx):
        ang=float(self.angHistory[idx])
        self.setResolution(ang)

"""
###
### Auxiliary class for positioning
###
class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
"""
