# -*- coding: latin-1 -*-
'''
[Name] Multi-axis alignment brick

[Description]

This brick display pad to control one to n motors.

[Properties]
----------------------------------------------------------------------
| name                | type     | description
----------------------------------------------------------------------
| mnemonic            | string       | could be a simple spec motor,a sample stage HWR,a MultiAxis HWR or an equipment. For all equipment, this brick use role ('horizontal','vertical','rotation') to define on which pad arrow the motor will be affected.
| title               | string       | the title of the brick
| formatString        | formatString | position motor format
| horizontalLayout    | boolean      | for multipad the layout direction
| steps               | string       | a step list separate by space
| arrow/motormove     | combo        | link motor movement with arrow (which direction is a positive move)
----------------------------------------------------------------------
'''

__version__ = 1.1
__author__ = "Sébastien Petitdemange"

__category__ = 'Motor'

import logging
import qt
import sys
import re
from BlissFramework.Utils import PropertyBag
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons

from Qub.Widget.QubPad import QubPad
from Qub.Widget.QubPad import QubPadPlug

class _stopIdle(qt.QTimer) :
    def __init__(self) :
        qt.QTimer.__init__(self)
        self.__motors = {}
        self.connect(self,qt.SIGNAL('timeout()'),self.__stopMotor);
    def addStopMotor(self,motor) :
        self.__motors[id(motor)] = motor
    def idle(self) :
        if not self.isActive() :
            self.start(0)
    def __stopMotor(self) :
        for motor in self.__motors.itervalues() :
            motor.stop()
        self.__motors = {}
            
class _AxisPlug(QubPadPlug) :
    def __init__(self,brick,horizontalMotor,verticalMotor,rotationMotor) :
        QubPadPlug.__init__(self)
        self.__horizontalMotor = horizontalMotor
        self.__verticalMotor = verticalMotor
        self.__rotationMotor = rotationMotor
        self.__brick = brick

        self.__hFactor = 1
        self.__vFactor = 1
        self.__rFactor = 1
        
    def close(self) :
        if self.__verticalMotor is not None :
            self.__brick.disconnect(self.__verticalMotor, qt.PYSIGNAL("stateChanged"), self.__updateVMotorState)
            self.__brick.disconnect(self.__verticalMotor, qt.PYSIGNAL("positionChanged"), self.__updateVMotorPosition)
        if self.__horizontalMotor is not None :
            self.__brick.disconnect(self.__horizontalMotor, qt.PYSIGNAL("stateChanged"), self.__updateHMotorState)
            self.__brick.disconnect(self.__horizontalMotor, qt.PYSIGNAL("positionChanged"), self.__updateHMotorPosition)
        if self.__rotationMotor is not None :
            self.__brick.disconnect(self.__rotationMotor, qt.PYSIGNAL("stateChanged"), self.__updateHMotorState)
            self.__brick.disconnect(self.__rotationMotor, qt.PYSIGNAL("positionChanged"), self.__updateHMotorPosition)

    def setFormat(self,useFormat) :
        self._padButton.getPad().setHFormat(str(useFormat))
        self._padButton.getPad().setVFormat(str(useFormat))
        self._padButton.getPad().setRFormat(str(useFormat))
        
    def init(self) :
        if self.__verticalMotor is not None :
            self._padButton.getPad().setVAxisName(self.__verticalMotor.userName())
            self.__brick.connect(self.__verticalMotor, qt.PYSIGNAL("stateChanged"), self.__updateVMotorState)
            self.__brick.connect(self.__verticalMotor, qt.PYSIGNAL("positionChanged"), self.__updateVMotorPosition)
 
        if self.__horizontalMotor is not None :
            self._padButton.getPad().setHAxisName(self.__horizontalMotor.userName())
            self.__brick.connect(self.__horizontalMotor, qt.PYSIGNAL("stateChanged"), self.__updateHMotorState)
            self.__brick.connect(self.__horizontalMotor, qt.PYSIGNAL("positionChanged"), self.__updateHMotorPosition)

        if self.__rotationMotor is not None :
            self._padButton.getPad().setRAxisName(self.__rotationMotor.userName())
            self.__brick.connect(self.__rotationMotor, qt.PYSIGNAL("stateChanged"), self.__updateRMotorState)
            self.__brick.connect(self.__rotationMotor, qt.PYSIGNAL("positionChanged"), self.__updateRMotorPosition)

    def setHArrowMotorMove(self,ArrowMotorMove) :
        self.__hFactor = ArrowMotorMove == "positive2right" or -1
    def setVArrowMotorMove(self,ArrowMotorMove) :
        self.__vFactor = ArrowMotorMove == "positive2up" or -1
    def setRArrowMotorMove(self,ArrowMotorMove) :
        self.__rFactor = ArrowMotorMove == "clockwise" or -1
 
        
    def up(self,step):
        self.__verticalMotor.moveRelative(step * self.__vFactor)
    def down(self,step):
        self.__verticalMotor.moveRelative(-step * self.__vFactor)
    def moveVertical(self,pos) :
        self.__verticalMotor.move(pos)

    def left(self,step):
        self.__horizontalMotor.moveRelative(-step * self.__hFactor)
    def right(self,step):
        self.__horizontalMotor.moveRelative(step * self.__hFactor)
    def moveHorizontal(self,pos) :
        self.__horizontalMotor.move(pos)
        
    def clockwise(self,step) :
        self.__rotationMotor.moveRelative(step * self.__rFactor)
    def unclockwise(self,step) :
        self.__rotationMotor.moveRelative(-step * self.__rFactor)
    def moveRotation(self,pos) :
        self.__rotationMotor.move(pos)
        
    def stopVertical(self):
        self.__brick.stopIdle().addStopMotor(self.__verticalMotor)
        self.__brick.stopIdle().idle()

    def stopHorizontal(self) :
        self.__brick.stopIdle().addStopMotor(self.__horizontalMotor)
        self.__brick.stopIdle().idle()

    def stopRotation(self) :
        self.__brick.stopIdle().addStopMotor(self.__rotationMotor)
        self.__brick.stopIdle().idle()

    def __updateHMotorState(self,state) :
        if state == self.__horizontalMotor.READY :
            self._padButton.endHMotorMoving()
            self._padButton.hMotorConnected()
        elif state == self.__horizontalMotor.MOVING :
            self._padButton.hMotorExternalMove()
        elif state == self.__horizontalMotor.ONLIMIT :
            self._padButton.hMotorError()
        elif state < self.__horizontalMotor.READY :
            self._padButton.hMotorDisconnected()

                
    def __updateHMotorPosition(self,position):
       self._padButton.getPad().setHPos(position)

    def __updateVMotorState(self,state) :
        if state == self.__verticalMotor.READY :
            self._padButton.endVMotorMoving()
            self._padButton.vMotorConnected()
        elif state == self.__verticalMotor.MOVING :
            self._padButton.vMotorExternalMove()
        elif state == self.__verticalMotor.ONLIMIT :
            self._padButton.vMotorError()
        elif state < self.__verticalMotor.READY :
            self._padButton.vMotorDisconnected()

    def __updateVMotorPosition(self,position):
       self._padButton.getPad().setVPos(position)
            

    def __updateRMotorState(self,state) :
        if state == self.__rotationMotor.READY :
            self._padButton.endRMotorMoving()
            self._padButton.rMotorConnected()
        elif state == self.__rotationMotor.MOVING :
            self._padButton.rMotorExternalMove()
        elif state == self.__rotationMotor.ONLIMIT :
            self._padButton.rMotorError()
        elif state < self.__rotationMotor.READY :
            self._padButton.rMotorDisconnected()

    def __updateRMotorPosition(self,position):
       self._padButton.getPad().setRPos(position)
 


class MultiAxisAlignmentBrick(BlissWidget):
    def __init__(self, *args):
        """Constructor
        """
        BlissWidget.__init__(self, *args)

        self.__stopIdle = _stopIdle()
          
        # addProperty adds a property for the brick :
        #   - 1st argument is the name of the property ;
        #   - 2d argument is the type (one of string, integer, float, file, combo) ;
        #   - 3rd argument is the default value.
        # In some cases (e.g combo), the third argument is a tuple of choices
        # and the fourth argument is the default value.
        # When a property is changed, the propertyChanged() method is called.
        self.addProperty("mnemonic", "string", "")
        self.addProperty("title", "string", "")
        self.addProperty("formatString", "formatString", "###.##")
        self.addProperty('horizontalLayout','boolean',True)
        self.__horizontalLayout = False
        self.addProperty('dynamicProperties','',PropertyBag.PropertyBag(),hidden=True)
        
        # now we can "draw" the brick, i.e creating GUI widgets
        # and arranging them in a layout. It is the default appearance
        # for the brick (if no property is set for example)
        self.__lblTitle = qt.QLabel(self)
        self.__lblTitle.setAlignment(qt.Qt.AlignHCenter)
        self.__pads = []
        self.__plugs = []
        self.__padLayout = qt.QGridLayout(None,1,1)
        self.__padLayout.setSpacing(0)
        self.__padLayout.setMargin(0)
        
        layout = qt.QVBoxLayout(self,0,0)
        layout.addWidget(self.__lblTitle)
        layout.addLayout(self.__padLayout)
        self.__extPadid = re.compile('pad (\d+)')
    def stopIdle(self) :
        return self.__stopIdle
    
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'mnemonic':
            self.__plugs = []
            for pad in self.__pads :
                self.__padLayout.remove(pad)
            self.__pads = []
            equipment = self.getHardwareObject(newValue)
            if equipment is not None :
                if hasattr(equipment,'isSampleStage') :
                    for pad in equipment.getAxisList() :
                        self.__createOnePad(pad)
                elif hasattr(equipment, 'move'): 
                    self.__createOneAxis(equipment)
                else :
                    self.__createOnePad(equipment)
                    
                #clean properties
                propNames = []
                for propertyName,prop in self.propertyBag.properties.iteritems() :
                    if propertyName not in ['fontSize','mnemonic','title','formatString'] :
                        propNames.append(propertyName)
                if not self.isRunning() and oldValue is not None:
                    for propertyName in propNames :
                        self.delProperty(propertyName)
                        self.addProperty('dynamicProperties','',PropertyBag.PropertyBag(),hidden=True)
                    # Brick Property
                    if hasattr(equipment,'isSampleStage') :
                        for i,axis in enumerate(equipment.getAxisList()) :
                            self.__addNewProperty(axis,i,len(self.__pads) > 1)
                    elif equipment.__class__.__name__ == 'SpecMotor':
                        self.__addNewAxisProperty()
                    else:
                        self.__addNewProperty(equipment)
                self.propertyBag.properties.update(self['dynamicProperties'].properties)
                self.propertyBag.updateEditor()
                for name,prop in self['dynamicProperties'].properties.iteritems() :
                    self.__setDynamicProperty(name,prop.getValue())
            # refresh labels
                self["formatString"] = self.getProperty("formatString").getUserValue()
        elif property == 'title':
            self.__lblTitle.setText(newValue)
        elif property == 'formatString':
            for plug in self.__plugs :
                plug.setFormat(self["formatString"])
        elif property == 'horizontalLayout':
            for pad in self.__pads :
                self.__padLayout.remove(pad)
            self.__horizontalLayout = newValue
            if newValue :
                for i,pad in enumerate(self.__pads) :
                    self.__padLayout.addWidget(pad,0,i)
            else:
                for i,pad in enumerate(self.__pads) :
                    self.__padLayout.addWidget(pad,i,0)
        else:
            if self.__setDynamicProperty(property,newValue) :
                self['dynamicProperties'].getProperty(property).setValue(newValue)

    def sizeHint(self) :
        height = self.__lblTitle.sizeHint().height()
        width = self.__lblTitle.sizeHint().width()
        if self.__horizontalLayout:
            width = 0
            padHeight = 0
            for pad in self.__pads:
                padHeight = max(padHeight,pad.sizeHint().height())
            for pad in self.__pads:
                width += pad.sizeHint().width()
            height += padHeight
        else:
            for pad in self.__pads :
                height += pad.sizeHint().height()
                width = max(width,pad.sizeHint().width())
        rSize = qt.QSize(width,height)
        self.setMinimumSize(rSize)
        return rSize

    def close(self,aFlag) :
        if aFlag:
            for plug in self.__plugs :
                plug.close()
            self.__plugs = []
            self.__pads = []
        BlissWidget.close(self,aFlag)
        
    def __setDynamicProperty(self,property,newValue) :
        returnFlag = False
        padid = 0
        matchResult = self.__extPadid.search(property)
        if matchResult :
            padid = int(matchResult.group(1))
        AxisName = {'hori.' : 'setH','vert.' : 'setV','rot.' : 'setR'}
        for key,beginNameFunc in AxisName.iteritems() :
            if property.find(key) > -1:
                break
        if property.find('steps') > -1 :
            pad = self.__pads[padid]
            try :
                steps = [float(x) for x in newValue.split(' ')]
                eval('pad.%s%s(steps)' % (beginNameFunc,'Steps'))
                returnFlag = True
            except:
                logging.getLogger().error('steps must be a float list separate by space')
        elif property.find('arrow/motormove') > -1 :
            plug = self.__plugs[padid]
            eval('plug.%s%s(\'%s\')' % (beginNameFunc,'ArrowMotorMove',newValue))
            returnFlag = True
        elif property.find('init percent size') > -1 :
            pad = self.__pads[padid]
            pad.setPadSize(newValue)
            returnFlag = True
        return returnFlag

    def __setHardwareParam(self,equipment,pad,plug) :
        hsteps = equipment.getStepsByRole('horizontal')
        if not len(hsteps) :
            hsteps = [1.]               # default
        pad.setHSteps(hsteps)

        vsteps = equipment.getStepsByRole('vertical')
        if not len(vsteps) :
            vsteps = [1.]               # default
        pad.setVSteps(vsteps)

        rsteps = equipment.getStepsByRole('rotation')
        if not len(rsteps) :
            rsteps = [1.]               # default
        pad.setRSteps(rsteps)

        plug.setHArrowMotorMove(equipment.getArrowMotorMoveByRole('horizontal'))
        plug.setVArrowMotorMove(equipment.getArrowMotorMoveByRole('vertical'))
        plug.setRArrowMotorMove(equipment.getArrowMotorMoveByRole('rotation'))
        
    def __addNewProperty(self,equipment,padid = 0,addNumberFlag = False) :
        padstring = ''
        if addNumberFlag :
            padstring = 'pad %d :' % padid

        try :
            if equipment.getDeviceByRole('horizontal') is not None:
                stringsteps = '1. 2. 3.'
                defaultArrowDirection = 'positive2right'
                if hasattr(equipment,'isMultiAxis') :
                    stringsteps = ' '.join([str(x) for x in equipment.getStepsByRole('horizontal')])
                    defaultArrowDirection = equipment.getArrowMotorMoveByRole('horizontal')
                self['dynamicProperties'].addProperty('%s%s' % (padstring,"hori. steps"),"string",stringsteps)
                self['dynamicProperties'].addProperty('%s%s' % (padstring,"hori. arrow/motormove"), "combo",
                                                      ("positive2right", "negative2right"),defaultArrowDirection)
        except:
            pass
        try:
            if equipment.getDeviceByRole('vertical') is not None:
                stringsteps = '1. 2. 3.'
                defaultArrowDirection = 'positive2up'
                if hasattr(equipment,'isMultiAxis') :
                    stringsteps = ' '.join([str(x) for x in equipment.getStepsByRole('vertical')])
                    defaultArrowDirection = equipment.getArrowMotorMoveByRole('vertical')
                self['dynamicProperties'].addProperty('%s%s' % (padstring,"vert. steps"),"string",stringsteps)
                self['dynamicProperties'].addProperty('%s%s' % (padstring,"vert. arrow/motormove"), "combo",
                                                      ("positive2up", "negative2up"),defaultArrowDirection)
        except:
            pass
        try:
            if equipment.getDeviceByRole('rotation') is not None:
                stringsteps = '1. 2. 3.'
                defaultArrowDirection = 'clockwise'
                if hasattr(equipment,'isMultiAxis') :
                    stringsteps = ' '.join([str(x) for x in equipment.getStepsByRole('rotation')])
                    defaultArrowDirection = equipment.getArrowMotorMoveByRole('rotation')
                self['dynamicProperties'].addProperty('%s%s' % (padstring,"rot. steps"),"string",stringsteps)
                self['dynamicProperties'].addProperty('%s%s' % (padstring,"rot. arrow/motormove"),"combo",
                                                      ("clockwise", "counterclockwise"),defaultArrowDirection)
        except:
            pass
        try:
            self['dynamicProperties'].addProperty('%s%s' % (padstring,"init percent size"),"float",1.0)
        except:
            import traceback
            traceback.print_exc()

    def __createOneAxis(self,motor) :
        pad = QubPad(self)
        pad.setAxis(QubPad.HORIZONTAL_AXIS)
        plug = _AxisPlug(self,motor,None,None)
        pad.setPlug(plug)
        self["formatString"] = self.getProperty("formatString").getUserValue()
        plug.init()
        self.__pads.append(pad)
        self.__plugs.append(plug)
        self.__padLayout.addWidget(pad,0,0)

    def __addNewAxisProperty(self) :
        padstring = 'pad 0 :'
        self['dynamicProperties'].addProperty('%s%s' % (padstring,"hori. steps"),"string",'1.')
        self['dynamicProperties'].addProperty('%s%s' % (padstring,"init percent size"),"float",1.0)
        
    def __createOnePad(self,equipment) :
        plug,pad = self.__createPlugNPad(equipment)
        if pad is not None and plug is not None :
            if hasattr(equipment,'isMultiAxis') :
                self.__setHardwareParam(equipment,pad,plug)
            self.__pads.append(pad)
            self.__plugs.append(plug)
            hlayout = self.getProperty('horizontalLayout')
            if hlayout and hlayout.value :
                self.__padLayout.addWidget(pad,0,len(self.__pads))
            else :
                self.__padLayout.addWidget(pad,len(self.__pads),0)
        
    def __createPlugNPad(self,equipment) :
         try:
             verticalMotor = equipment.getDeviceByRole("vertical")
         except :
             verticalMotor = None
         try:
             horizontalMotor = equipment.getDeviceByRole("horizontal")
         except :
             horizontalMotor = None
         try :
             rotationMotor = equipment.getDeviceByRole('rotation')
         except :
             rotationMotor = None
                    
         pad,plug = None,None
         if verticalMotor is None and horizontalMotor is None and rotationMotor is None :
             logging.getLogger().error("%s: could not find vertical or horizontal or rotation motors in Hardware Object %s",
                                       str(self.name()), equipment.name())
         else :
             pad = QubPad(self)
             padAxisType = 0
             if verticalMotor is not None :
                 padAxisType |= QubPad.VERTICAL_AXIS
             if horizontalMotor is not None :
                 padAxisType |= QubPad.HORIZONTAL_AXIS
             if rotationMotor is not None :
                 padAxisType |= QubPad.ROTATION_AXIS
             pad.setAxis(padAxisType)
             plug = _AxisPlug(self,horizontalMotor,verticalMotor,rotationMotor)
             pad.setPlug(plug)
             # refresh labels
             self["formatString"] = self.getProperty("formatString").getUserValue()
             plug.init()       
         return (plug,pad)

     


