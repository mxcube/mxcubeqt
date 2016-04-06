"""
Camera Tools Brick

[Description]

Thiss brick allows to define action to be done on a CameraBrick object.
It does not deal with Camera associated motors as CameraMotorToolsBrick
should do it.
Available tools are the following:

add a list in the tool bar or in the menu to selected camera from a Meteor2
server
    
[Properties]

Falcon Select - ("None","Toolbar","Popup") - allow to select the different
                                             camera connected to a falcon
                                             acquisition card. Place
                                             "Falcon Select" action in
                                             toolbar or popup menu of the
                                             camera brick
Falcon - string - falcon hardware object for "Falcon Select" mode
Falcon # - integer - Number of camera connected to the falcon board


[Signals]

getView - {"drawing"} - emitted to get a reference on the image viewer object.
                        At returned of the emit function, the key "drawing"
                        exists and its value is the reference of the image
                        viewer or the key "drawing" does not exists which mean
                        that the image viewer object does not exist.


[Slots]

                                                 
[Comments]


"""
import qt
import sys
import qttable
import qtcanvas
import logging

from BlissFramework.BaseComponents import BlissWidget

from Qub.Widget.QubActionSet import QubRulerAction
from Qub.Widget.QubActionSet import QubSelectPointAction
from Qub.Widget.QubActionSet import QubListAction

__category__ = "Camera"

#############################################################################
##########                                                         ##########
##########                         BRICK                           ##########
##########                                                         ##########       
#############################################################################       
class CameraToolsBrick(BlissWidget):
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)
        
        """
        variables
        """        
        self.view = None
        self.firstCall = True

        """
        property
        """
        """
        falcon select mode properties
        """
        self.addProperty("Falcon Select", "combo",
                         ("none", "toolbar", "popup"), "none")
        self.falconMode = None
        self.falconAction = None
                
        self.addProperty("Falcon", "string", "")
        self.falconHwo = None

        self.addProperty("Falcon #", "integer", 1)
        self.falconNumber = None
                
        """
        Signal
        """
        self.defineSignal('getView',())
 
        """
        Slot
        """

        """
        widgets - NO APPEARANCE
        """
        self.setFixedSize(0, 0)
                        
               
    def propertyChanged(self, prop, oldValue, newValue):
        """
        FALCON
        """
        if prop == "Falcon Select":
            self.falconMode = newValue
            if newValue == "none":
                self.falconMode = None
            if newValue == "popup":
                self.falconMode = "contextmenu"
            
        if prop == "Falcon":
            self.falconHwo = self.getHardwareObject(newValue)

        if prop == "Falcon #":
            self.falconNumber = newValue
        
        if not self.firstCall:
            self.configureAction()
            
    def run(self):
        """
        get view
        """
        view = {}
        self.emit(qt.PYSIGNAL("getView"), (view,))
        try:
            self.drawing = view["drawing"]
            self.view = view["view"]        
        except:
            print("No View")
                    
        self.configureAction()
        
        self.firstCall = False
    
    def configureAction(self):
        """
        FALCON
        """
        if self.falconMode is not None:
            if self.falconAction is None and self.falconNumber > 1:
                """
                create action
                """
                cameras = []
                for i in range(self.falconNumber):
                    cameras.append("Camera %d"%i)
                    
                self.falconAction = QubListAction(items=cameras,
                                                  name='Select Falcon Camera',
                                                  place=self.falconMode,
                                                  actionInfo = 'Select Falcon Camera',
                                                  group='Tools')
                self.connect(self.falconAction, qt.PYSIGNAL("ItemSelected"),
                             self.cameraSelected)
                    
                if self.view is not None:
                    actions = []
                    actions.append(self.falconAction)
                    self.view.addAction(actions)
        else:
            if self.falconAction is not None:
                """
                remove action
                """
                if self.view is not None:
                    self.view.delAction(["Select Falcon Camera",])
                    
                """
                del action from view
                """
                self.disconnect(self.falconAction, qt.PYSIGNAL("ItemSelected"),
                                self.cameraSelected)
                self.falconAction = None

        if self.falconHwo is not None:
            try:
                data = {'type':'tango','name':'VideoInput'}
                vi = self.falconHwo.addChannel(data,'VideoInput')
                videoinput = self.falconHwo.getChannelObject("VideoInput")
                val = int(videoinput.getValue())
                self.falconAction.setItemIndex(val - 1)
            except:
                s = "Cannot get video input attribute"
                logging.getLogger("Brick").error(s)
        else:
            logging.getLogger("Brick").error("No Falcon defined")
                        
    """
    FALCON
    """                                                           
    def cameraSelected(self, idx, camera):
        if self.falconHwo is not None:
            try:
                self.falconHwo.getChannelObject("VideoInput").setValue(idx+1)
            except:
                logging.getLogger("Brick").error("Cannot set video input attribute")
         
