
import logging
from PyQt4 import QtCore, QtGui

from Qt4_SampleChangerBrick3 import Qt4_SampleChangerBrick3, BasketView, VialView

from Qt4_sample_changer_helper import *


__category__ = "ALBA"

class Qt4_ALBA_SampleChangerBrick(Qt4_SampleChangerBrick3):
    def __init__(self, *args):
        Qt4_SampleChangerBrick3.__init__(self,*args)
        self._pathRunning = None
        self._poweredOn = None
        self.device = None
        self.has_basket_HT = None

        logging.getLogger("GUI").info("ALBA Sample Changer") 

        self.addProperty("use_basket_HT", "boolean", False)

    def propertyChanged(self, property_name, oldValue, newValue):
        logging.getLogger("GUI").info("Property Changed: " + str(property_name) + " = " + str(newValue))


        if property_name == 'mnemonic':
            if self.sample_changer_hwobj is not None:
                self.disconnect(self.device, 'runningStateChanged', self._updatePathRunning)
                self.disconnect(self.device, 'powerStateChanged', self._updatePowerState)

        Qt4_SampleChangerBrick3.propertyChanged(self, property_name, oldValue, newValue)

        if property_name == 'mnemonic':
            # load the new hardware object
      
            if self.sample_changer_hwobj is not None:
                self.connect(self.sample_changer_hwobj, 'runningStateChanged', self._updatePathRunning)
                self.connect(self.sample_changer_hwobj, 'powerStateChanged', self._updatePowerState)
           
                self._poweredOn = self.sample_changer_hwobj.isPowered()
                self._pathRunning = self.sample_changer_hwobj.isPathRunning()
                self._updateButtons()

            self.operations_widget.show()

            self.switch_to_sample_transfer_button.hide()
            self.test_sample_changer_button.hide()
            self.scan_baskets_view.hide()
            self.current_basket_view.hide()
            self.current_sample_view.hide()
            self.reset_baskets_samples_button.hide()
            self.double_click_loads_cbox.hide()

            self.status.sc_can_load_radiobutton.hide()
            self.status.reset_button.hide()
            self.status.minidiff_can_move_radiobutton.hide()

        elif property_name == 'basketCount':
            if self.has_basket_HT:
                self.add_basket_HT()
        elif property_name == 'use_basket_HT':
            logging.getLogger("GUI").info("has HT basket %s" %(newValue))
            if newValue:
                if self.basket_count is not None:
                    self.has_basket_HT = True
                    self.add_basket_HT()
                else:
                    self.has_basket_HT = True


    def build_operations_widget(self):
        self.buttons_layout = QtGui.QHBoxLayout()
        self.operation_buttons_layout = QtGui.QVBoxLayout()

        self.load_button = QtGui.QPushButton("Load", self)
        self.unload_button = QtGui.QPushButton("Unload", self)
        self.abort_button = QtGui.QPushButton("Abort", self)

        self.load_button.clicked.connect(self.load_selected_sample)
        self.unload_button.clicked.connect(self.unload_selected_sample)
        self.abort_button.clicked.connect(self.abort_mounting)

        self.buttons_layout.addWidget(self.load_button)
        self.buttons_layout.addWidget(self.unload_button)
        self.operation_buttons_layout.addLayout(self.buttons_layout)
        self.operation_buttons_layout.addWidget(self.abort_button)
        self.operations_widget.setLayout(self.operation_buttons_layout)

    def add_basket_HT(self):
        # add one extra basket (next row, first colum) for HT samples. basket index is 100
        temp_basket = BasketView(self.sc_contents_gbox, 100)
        basket_row = int(self.basket_count / self.basket_per_column) + 1
        basket_column = 0
        logging.getLogger("GUI").info("adding HT basket %s/%s" %(basket_row,basket_column))
        QtCore.QObject.connect(temp_basket, QtCore.SIGNAL("load_this_sample"),self.load_this_sample)
        QtCore.QObject.connect(temp_basket, QtCore.SIGNAL("select_this_sample"),self.select_this_sample)
        temp_basket.setChecked(False)
        temp_basket.setEnabled(True)
        temp_basket.setUnselectable(False)
        self.baskets.append(temp_basket)
        self.basket_grid_layout.addWidget(temp_basket, basket_row, basket_column)

    def infoChanged(self):
         
        Qt4_SampleChangerBrick3.infoChanged(self)

        if self.has_basket_HT:
             vials = [[VialView.VIAL_BARCODE]] *10 
             self.baskets[-1].setMatrices(vials)

    def sc_state_changed(self, state, previous_state=None):
        
        Qt4_SampleChangerBrick3.sc_state_changed(self, state, previous_state)

        self.state = state
        self._updateButtons()

        #self.load_button.setEnabled(SC_STATE_GENERAL.get(state, False))
        #self.unload_button.setEnabled(SC_STATE_GENERAL.get(state, False))
        #self.abort_button.setEnabled(SC_STATE_GENERAL.get(state, False))

    def _updatePowerState(self, value):
        self._poweredOn = value
        logging.getLogger("GUI").info("POwer state changed : %s " % (value))
        self._updateButtons()

    def _updatePathRunning(self, value):
        logging.getLogger("GUI").info("Path RUnning changed : %s " % (value))
        self._pathRunning = value
        self._updateButtons()

    def _updateButtons(self):
        logging.getLogger("GUI").info("Update buttons %s / %s  / %s " % (self.state, self._poweredOn, self._pathRunning))
        
        running = self._pathRunning and True or False
        ready = not running
        poweredOn = self._poweredOn and True or False # handles init state None as False

        if not poweredOn:
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = str(Qt4_widget_colors.LIGHT_GRAY.name())
        elif ready:
            self.load_button.setEnabled(True)
            self.unload_button.setEnabled(True)
            self.abort_button.setEnabled(False)
            abort_color = str(Qt4_widget_colors.LIGHT_GRAY.name())
        else:
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(True)
            abort_color = str(Qt4_widget_colors.LIGHT_RED.name())

        self.abort_button.setStyleSheet("background-color: %s;" % abort_color)

    def load_selected_sample(self):
        logging.getLogger("GUI").info("Loading sample basket: %s / %s" % (self.selected_basket, self.selected_vial))
        basket = self.selected_basket
        vial = self.selected_vial
        if basket is not None and vial is not None:
            if basket != 100:
                sample_loc=(basket,vial)
                self.sample_changer_hwobj.load(sample_loc,wait=False)
            else:
                logging.getLogger("GUI").info("Is an HT sample: idx=%s (not implemented yet)" % (self.selected_vial))

    def unload_selected_sample(self):
        logging.getLogger("GUI").info("Unloading sample basket: %s / %s" % (self.selected_basket, self.selected_vial))
        #self.sample_changer_hwobj.load(holder_len,None,sample_loc,self.sampleLoadSuccess,self.sampleLoadFail, wait=False)
        self.sample_changer_hwobj.unload(holder_len,matrix_code,location,self.sampleUnloadSuccess,self.sampleUnloadFail,wait=False)

    def abort_mounting(self):
        self.sample_changer_hwobj._doAbort() 
