#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.
"""
File: Qt4_CatsSimpleBrick.py

Description
-------------
The Qt4_CatsSimpleBrick.py is a simplified version of the Qt4_SampleChangerBrick3.py

It presents the samples in the same way as Qt4_SampleChangerBrick3.py. It allows to
select a sample by single clicking on it then perform the Load/Unload and Abort
operations on the Cats sample changer.

The Qt4_CatsSimpleBrick.py adds a new property "use_basket_HT", to declare a "High Temperature"
puck. This HT puck has special handling by the Cats sample changer.

"""

import logging

from QtImport import *

from Qt4_SampleChangerBrick3 import Qt4_SampleChangerBrick3, BasketView, VialView
from Qt4_sample_changer_helper import *
from BlissFramework.Qt4_BaseComponents import BlissWidget

__category__ = "Sample changer"

class CatsStatusView(QGroupBox, BlissWidget):

    def __init__(self, parent, brick):
        
        QGroupBox.__init__(self, "State", parent)
        BlissWidget.__init__(self, parent)
        # Graphic elements ----------------------------------------------------
        #self.contents_widget = QGroupBox("Sample Changer State", self)

        self._parent = brick
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Layout --------------------------------------------------------------

        _layout = QHBoxLayout(self)
        _layout.addWidget(self.status_label)
        _layout.setSpacing(2)
        _layout.setContentsMargins(6,6,6,10)

    def setStatusMsg(self, status):
        self.status_label.setToolTip(status)
        status = status.strip()
        self.setToolTip(status)

    def setState(self, state):
       
        logging.getLogger().debug("SC StatusView. State changed %s" % str(state))
        color = SC_STATE_COLOR.get(state, None)

        if color is None:
            color = Qt4_widget_colors.LINE_EDIT_ORIGINAL
        
        Qt4_widget_colors.set_widget_color(self.status_label, color)

        enabled = SC_STATE_GENERAL.get(state, False)
        self.status_label.setEnabled(enabled)
        state_str = SampleChangerState.tostring(state)
        self.status_label.setText(state_str)
        self._parent.set_status_info("sc", state_str)
       
    def setIcons(self, *args):
        pass

class Qt4_CatsSimpleBrick(Qt4_SampleChangerBrick3):

    def __init__(self, *args):
        Qt4_SampleChangerBrick3.__init__(self,*args)

        self.device = None  
        self.has_basket_HT = None 

        self._pathRunning = None
        self._poweredOn = None

        self.addProperty("use_basket_HT", "boolean", False)

        # display operations widget
        self.operations_widget.show()

        # remove all unwanted controls 
        self.switch_to_sample_transfer_button.hide()
        self.test_sample_changer_button.hide()
        self.scan_baskets_view.hide()
        self.current_basket_view.hide()
        self.current_sample_view.hide()
        self.reset_baskets_samples_button.hide()
        self.double_click_loads_cbox.hide()

    def propertyChanged(self, property_name, oldValue, newValue):
        if property_name == 'mnemonic':
            if self.sample_changer_hwobj is not None:
                self.disconnect(self.device, 'runningStateChanged', \
                         self._updatePathRunning)
                self.disconnect(self.device, 'powerStateChanged', \
                         self._updatePowerState)

        Qt4_SampleChangerBrick3.propertyChanged(self, property_name, \
                         oldValue, newValue)

        if property_name == 'mnemonic':
            # load the new hardware object
      
            if self.sample_changer_hwobj is not None:
                self.connect(self.sample_changer_hwobj, 'runningStateChanged',\
                               self._updatePathRunning)
                self.connect(self.sample_changer_hwobj, 'powerStateChanged', \
                               self._updatePowerState)
           
                self._poweredOn = self.sample_changer_hwobj.isPowered()
                self._pathRunning = self.sample_changer_hwobj.isPathRunning()
                self._updateButtons()

        elif property_name == 'basketCount':
            # make sure that HT basket is added after Parent class has created all baskets
            if self.has_basket_HT:
                self.add_basket_HT()
        elif property_name == 'use_basket_HT':
            if newValue:
                if self.basket_count is not None:
                    self.has_basket_HT = True
                    self.add_basket_HT()
                else:
                    self.has_basket_HT = True


    def build_status_view(self, container):
        return CatsStatusView(container, self)

    def build_operations_widget(self):
        self.buttons_layout = QHBoxLayout()
        self.operation_buttons_layout = QVBoxLayout()

        self.load_button = QPushButton("Load", self)
        self.unload_button = QPushButton("Unload", self)
        self.abort_button = QPushButton("Abort", self)

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
        ht_basket = BasketView(self.sc_contents_gbox, 100)
        ht_basket.setChecked(False)
        ht_basket.setEnabled(True)
        ht_basket.set_title("HT")
        ht_basket.selectSampleSignal.connect(self.user_select_this_sample)
        self.baskets.append(ht_basket)

        basket_row = int(self.basket_count / self.basket_per_column) + 1
        basket_column = 0
        self.baskets_grid_layout.addWidget(ht_basket, basket_row, basket_column)

    def select_sample(self, basket_no, sample_no):
        if self.has_basket_HT and basket_no == 100:
            basket_no = -1

        Qt4_SampleChangerBrick3.select_sample(self, basket_no, sample_no)

    def infoChanged(self):
         
        Qt4_SampleChangerBrick3.infoChanged(self)

        if self.has_basket_HT:
             vials = [[VialView.VIAL_BARCODE]] *10 
             self.baskets[-1].set_matrices(vials)

    def sc_state_changed(self, state, previous_state=None):
        logging.getLogger().debug("SC State changed %s" % str(state))
        Qt4_SampleChangerBrick3.sc_state_changed(self, state, previous_state)

        self.state = state
        self._updateButtons()

    def _updatePowerState(self, value):
        self._poweredOn = value
        self._updateButtons()

    def _updatePathRunning(self, value):
        self._pathRunning = value
        self._updateButtons()

    def _updateButtons(self):
        running = self._pathRunning and True or False

        if self.state in [SampleChangerState.Ready, SampleChangerState.StandBy]:
            ready = not running
        else:
            ready = False

        poweredOn = self._poweredOn and True or False # handles init state None as False

        logging.getLogger().debug("updating buttons %s / %s / %s" % (running, poweredOn, self.state))

        if not poweredOn:
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = Qt4_widget_colors.LIGHT_GRAY
        elif ready:
            logging.getLogger().info("Qt4_CatsSimpleBrick update buttons (ready)")
            self.load_button.setEnabled(True)
            if self.sample_changer_hwobj.hasLoadedSample():
                self.unload_button.setEnabled(True)
            else:
                self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(False)
            abort_color = Qt4_widget_colors.LIGHT_GRAY
        else:
            logging.getLogger().info("Qt4_CatsSimpleBrick update buttons (other)")
            self.load_button.setEnabled(False)
            self.unload_button.setEnabled(False)
            self.abort_button.setEnabled(True)
            abort_color = Qt4_widget_colors.LIGHT_RED

        self.abort_button.setStyleSheet("background-color: %s;" % abort_color.name())

        #Qt4_widget_colors.set_widget_color(self.abort_button, abort_color)

    def load_selected_sample(self):

        basket, vial = self.user_selected_sample
        logging.getLogger("GUI").info("Loading sample: %s / %s" % (basket, vial))

        if basket is not None and vial is not None:
            if basket != 100:
                sample_loc="%d:%02d" % (basket+1,vial)
                self.sample_changer_hwobj.load(sample_loc,wait=False)
            else:
                self.sample_changer_hwobj.load_ht(vial,wait=False)
                logging.getLogger("GUI").info("Is an HT sample: idx=%s (not implemented yet)" % (vial))

    def unload_selected_sample(self):
        logging.getLogger("GUI").info("Unloading sample") 
        self.sample_changer_hwobj.unload()

    def abort_mounting(self):
        self.sample_changer_hwobj._doAbort() 

def test_brick(brick):
    brick.propertyChanged("use_basket_HT", None, True)
    brick.propertyChanged("singleClickSelection", None, True)
    brick.propertyChanged("basketCount", None, "9:3")
