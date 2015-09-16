"""
[Name] PlateManipulator

[Description]
Plate manipulator hardware object is used to use diffractometer in plate mode.
It is compatable with md2, md3 diffractometers. Class is based on 
SampleChanger, so it has all the sample changed functionalities, like
mount, unmount sample (in this case move to plate position).
Plate is organized in rows and columns. Each cell (Cell) contains drop (Drop).
Each drop could contain several crystals (Xtal). If CRIMS is available then
each drop could have several crystals.

[Channels]

 - self.chan_current_phase   : diffractometer phase 
 - self.chan_plate_location  : plate location (col, row)
 - self.chan_state           : diffractometer state

[Commands]

 - self.cmd_move_to_location : move to plate location

[Emited signals]

 - emited signals defined in SampleChanger class 

[Included Hardware Objects]
-----------------------------------------------------------------------
| name            | signals          | functions
-----------------------------------------------------------------------
-----------------------------------------------------------------------
"""
import logging

from sample_changer import Crims
from sample_changer.GenericSampleChanger import *

class Xtal(Sample):
    __NAME_PROPERTY__ = "Name"
    __LOGIN_PROPERTY__ = "Login"

    def __init__(self,drop, index):
        super(Xtal, self).__init__(drop, Xtal._getXtalAddress(drop, index), False)
        self._setImageX(None)
        self._setImageY(None)
        self._setImageURL(None)
        self._setName(None)
        self._setLogin(None)
        self._setInfoURL(None)

        self._setInfo(False, False, False)
        self._setLoaded(False, False)

    def _setName(self,value):
        self._setProperty(self.__NAME_PROPERTY__,value)

    def getName(self):
        return self.getProperty(self.__NAME_PROPERTY__)

    def _setLogin(self,value):
        self._setProperty(self.__LOGIN_PROPERTY__,value)

    def getLogin(self):
        return self.getProperty(self.__LOGIN_PROPERTY__)

    def getDrop(self):
        return self.getContainer()

    def getCell(self):
        return self.getDrop().getCell()

    @staticmethod
    def _getXtalAddress(well, index):
        return str(well.getAddress()) + "-" + str(index)

class Drop(Container):
    __TYPE__ = "Drop"
    def __init__(self,cell, well_no):
        super(Drop, self).__init__(self.__TYPE__,cell, Drop._getWellAddress(cell, well_no), False)
         
    @staticmethod
    def _getWellAddress(cell, well_no):
        return str(cell.getAddress()) + ":" + str(well_no)

    def getCell(self):
        return self.getContainer()

    def getWellNo(self):
        return self.getIndex() + 1

    def isLoaded(self):
        """
        Returns if the sample is currently loaded for data collection 
        :rtype: bool
        """
        sample = self.getSample()
        return sample.isLoaded()  
 
    def getSample(self):
        """
        In this cas we assume that there is one crystal per drop
        """ 
        sample = self.getComponents()
        return sample[0]
 

class Cell(Container):
    __TYPE__ = "Cell"
    def __init__(self, container, row, col, wells):
        super(Cell, self).__init__(self.__TYPE__,container,Cell._getCellAddress(row,col),False)
        self._row=row
        self._col=col
        self._wells=wells
        for i in range(wells):
            drop = Drop(self, i + 1)
            self._addComponent(drop)
            xtal = Xtal(drop,drop.getNumberOfComponents())
            drop._addComponent(xtal)
        self._transient=True

    def getRow(self):
        return self._row

    def getRowIndex(self):
        return ord(self._row.upper()) - ord('A')

    def getCol(self):
        return self._col

    def getWellsNo(self):
        return self._wells

    @staticmethod
    def _getCellAddress(row, col):
        return str(row) + str(col)


class PlateManipulator(SampleChanger):
    """
    """    
    __TYPE__ = "PlateManipulator"    

    def __init__(self, *args, **kwargs):
        super(PlateManipulator, self).__init__(self.__TYPE__,False, *args, **kwargs)

        self.num_cols = None
        self.num_rows = None
        self.num_drops = None
        self.current_state = None
        self.current_phase = None
        self.current_location = None
        self.reference_pos_x = None

        self.crims_url = None
        self.cmd_move_to_location = None
        self.chan_current_phase = None
        self.chan_plate_location = None
        self.chan_state = None
       
        self.camera_hwobj = None 
            
    def init(self):      
        """
        Descript. :
        """
        self.num_cols = self.getProperty("numColls")
        self.num_rows = self.getProperty("numRows")
        self.num_drops = self.getProperty("numDrops")
        self.reference_pos_x = self.getProperty("referencePosX") 
        if not self.reference_pos_x:
            self.reference_pos_x = 0.5
        self.crims_url = self.getProperty("crimsWsRoot")

        self._initSCContents()
        self.cmd_move_to_location = self.getCommandObject("startMovePlateToLocation")
        self.chan_current_phase = self.getChannelObject("CurrentPhase")
        if self.chan_current_phase:
            self.chan_current_phase.connectSignal("update", self.current_phase_changed)

        self.chan_plate_location = self.getChannelObject("PlateLocation")
        if self.chan_plate_location is not None:
            self.chan_plate_location.connectSignal("update", self.current_location_changed)

        self.chan_state = self.getChannelObject("State")
        if self.chan_state is not None:
            self.chan_state.connectSignal("update", self._onStateChanged)

        self.camera_hwobj = self.getDeviceByRole("camera") 
        if not self.camera_hwobj:
            logging.getLogger("HWR").warning('PlateManipulator: camera hwobj not defined')   
       
        SampleChanger.init(self)

        self.current_phase_changed('Centring')
        self._onStateChanged('Ready')
 

    def current_phase_changed(self, phase):
        self.current_phase = phase
        self._onStateChanged(self.current_state)  

    def plate_location_changed(self, location):
        """
        Descript. : col, row, x, y
        """
        self.current_location = location
        self._updateLoadedSample()
        
    def _onStateChanged(self, state):
        """
        Descript. : state change callback. Based on diffractometer state
                    sets PlateManipulator state.
        """
        self.current_state = state

        if state is None:
            self._setState(SampleChangerState.Unknown)
        else:
            if   state == "Alarm": self._setState(SampleChangerState.Alarm)
            elif state == "Fault": self._setState(SampleChangerState.Fault)
            elif state == "Moving" or state == "Running": self._setState(SampleChangerState.Moving)
            elif state == "Ready":
                if self.current_phase == "Transfer":    self._setState(SampleChangerState.Charging)
                elif self.current_phase == "Centring":  self._setState(SampleChangerState.Ready)
                else:                                   self._setState(SampleChangerState.StandBy)
            elif state == "Initializing": self._setState(SampleChangerState.Initializing)

    def _initSCContents(self):
        """
        Descript. : Initializes content of plate.
        """
        self._setInfo(False, None, False)
        self._clearComponents()
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell = Cell(self, chr(65 + row), col + 1, self.num_drops)
                self._addComponent(cell)

    def _doAbort(self):
        """
        Descript. :
        """
        self._abort()

    def _doChangeMode(self,mode):
        """
        Descript. :
        """
        if mode == SampleChangerMode.Charging:
            self._set_phase("Transfer")
        elif mode == SampleChangerMode.Normal:
            self._set_phase("Centring")

    def _doLoad(self, element=None):
        """
        Descript. :
        """
        #Agree on which level to select
        selected=self.getSelectedSample()
        if (element is None):
            element = self.getSelectedSample()
        if (element is not None):
            if (element!=selected):
                #Here is actual move 
                self._doSelect(element)
            self._setLoadedSample(element)

    def _doUnload(self,sample_slot=None):
        """
        Descript. :
        """
        self._resetLoadedSample()

    def _doReset(self):
        """
        Descript. :
        """
        self._reset(False)
        self._waitDeviceReady(10)

    def _doScan(self,component, recursive):
        """
        Descript. :
        """
        if not isinstance(component, PlateManipulator):
            raise Exception ("Not supported")
        self._initializeData()
        if self.getToken() is None:
            raise Exception ("No plate barcode defined")
        self._loadData(self.getToken())

    def _loadData(self, barcode):
        pp = Crims.getProcessingPlan(barcode, self.crims_url)
       
        if pp is None:
            msg = "No information about plate with barcode %s found in CRIMS" % barcode
            logging.getLogger("user_level_log").error(msg) 
        else:
            msg = "Information about plate with barcode %s found in CRIMS" % barcode
            logging.getLogger("user_level_log").info(msg) 
            self._setInfo(True,pp.Plate.Barcode,True)

            for x in pp.Plate.Xtal:
                cell = self.getComponentByAddress(Cell._getCellAddress(x.Row, x.Column))
                cell._setInfo(True,"",True)
                drop = self.getComponentByAddress(Drop._getWellAddress(cell,x.Shelf))
                drop._setInfo(True,"",True)
                xtal = Xtal(drop,drop.getNumberOfComponents())
                xtal._setInfo(True,x.PinID,True)
                xtal._setImageURL(x.IMG_URL)
                xtal._setImageX(x.offsetX)
                xtal._setImageY(x.offsetY)
                xtal._setLogin(x.Login)
                xtal._setName(x.Sample)
                xtal._setInfoURL(x.SUMMARY_URL)
                drop._addComponent(xtal)
            return pp

    def _doSelect(self,component):
        """
        Descript. :
        """
        if isinstance(component, Xtal):
            col = xtal.Column
            row = ord(component.Row.upper()) - ord('A')
            #TODO add image maching here
            pos_x = 0.5
            pos_y = 0.5
            #location = [row, xtal.Column, pos_x, pos_y]
            component.getContainer()._setSelected(True)
            component.getContainer().getContainer()._setSelected(True)
        elif isinstance(component, Drop):
            row = component.getCell().getRowIndex()
            col = component.getCell().getCol() - 1
            pos_x = self.reference_pos_x
            pos_y = component.getWellNo() / float(self.num_drops + 1)
            component._setSelected(True)
            component.getContainer().getContainer()._setSelected(True)
        elif isinstance(component, Cell):
            row = component.getRowIndex()
            col = component.getCol()-1
            pos_x = self.reference_pos_x
            pos_y = 0.5
            component._setSelected(True)
        else:
            raise Exception ("Invalid selection")

        if self.cmd_move_to_location:
            self.cmd_move_to_location(row, col, pos_x, pos_y)
            self._resetLoadedSample()
            self._waitDeviceReady(10)
        else:
            #No actual move cmd defined. Act like a mockup
            drop_index = int(pos_y * (self.num_drops + 1))
            self.current_location = [row, col, pos_x, pos_y]
            self._onStateChanged('Ready')

    def _doUpdateInfo(self):
        """
        Descript. :
        """
        #self._updateState()
        #Remove if callback works
        self._updateLoadedSample()

    def _updateLoadedSample(self):
        """
        Descript. : function to update plate location. It is called by 1 sec
                    timer. 
        """
        if self.current_location is not None:
            row = self.current_location[0]
            col = self.current_location[1]
            y_pos = self.current_location[3]
            drop_index = abs(y_pos * self.num_drops) + 1
            if drop_index > self.num_drops:
                drop_index = self.num_drops
            cell = self.getComponentByAddress("%s%d" %(chr(65 + row), col + 1))
            if cell is None:
                return
            old_sample = self.getLoadedSample()
            drop = cell.getComponentByAddress("%s%d:%d" %(chr(65 + row), col + 1, drop_index))
            new_sample = drop.getSample()
            if old_sample != new_sample:
                if old_sample is not None:
                    # there was a sample on the gonio
                    old_sample._setLoaded(False, True)
                if new_sample is not None:
                    #self._updateSampleBarcode(new_sample)
                    new_sample._setLoaded(True, True)    

    def getSampleList(self):
        """
        Descript. :
        """
        sample_list = []
        for c in self.getComponents():
            if isinstance(c, Cell):
                for drop in c.getComponents():
                    #sample_list.append(drop)
                    sample_list.append(drop.getSample())
        return sample_list

    def get_plate_info(self):
        """
        Descript. : returns dict with plate info
        """
        plate_info_dict = {}
        plate_info_dict['num_cols'] = self.num_cols
        plate_info_dict['num_rows'] = self.num_rows
        plate_info_dict['num_drops'] = self.num_drops
        plate_info_dict['plate_label'] = "Demo plate label"
        return plate_info_dict

    def get_current_location(self):
        return self.current_location

    def sync_with_crims(self, barcode):
        return self._loadData(barcode)

    def _isDeviceBusy(self):
        return  self.getState() in (SampleChangerState.Moving, SampleChangerState.Initializing)

    def _isDeviceReady(self):
        return self.getState()  in (SampleChangerState.Ready, SampleChangerState.Charging)

    def _waitDeviceReady(self,timeout=-1):
        start=time.clock()
        while not self._isDeviceReady():
            if timeout>0:
                if (time.clock() - start) > timeout:
                    raise Exception("Timeout waiting device ready")
            gevent.sleep(0.01)
