#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""
[Name] Centering Brick

[Description]
This brick allows to center the sample in order it gets the closest
to the beam while it rotates with the 'phi' motor.

First, it gets data for calculating the final motor positions making
the user click several times on the 'same' sample point while it
rotates the phi motor 'N Centring Points' times 'Delta Phi' degrees

Then it calculates new motor positions and moves them.
Usually, at the end of the procedure the following motors are moved:
'sample y' and 'sample x' : motors on top of which is the sample
'phi' : rotation motor in top of which sampley and samplex are
'phiy', 'phiz' : translations motors on vertcal and horizontal axis

When the centring is finished, it displays on a matplotlib figure
the data used on the centring, and a visualization of the motor
movements

[Properties]

[Signals] -

centring_parameters_changed

[Slots] -

centring_started - connected to QtGraphicsManager centringStarted signal

centring_failed - connected to QtGraphicsManager centringFailed signal

centring_successful - connected to QtGraphicsManager centringSuccessful signal

image_clicked - connected to Diffractometer centring_image_clicked signal

show_centring_paremeters - connected to Diffractometer centring_calculation_ended signal


[Comments] -
See also sample_centring.py file in HardwareRepository git submodule

[Hardware Objects]
-----------------------------------------------------------------------
| name         | signals             | functions
-----------------------------------------------------------------------
|          | signal0     | function0()
|  	       
-----------------------------------------------------------------------
"""

import sys
import math
import logging
import numpy

from gui.utils import Icons, Colors, QtImport


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR
from HardwareRepository.HardwareObjects import sample_centring


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCenteringBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None

        # Internal values -----------------------------------------------------
        self.num_clicked_centring_pos = 0
        
        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------
        self.define_signal("centring_parameters_changed", ())

        # Slots ---------------------------------------------------------------
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Sample centering", self)
        self.ui_widgets_manager = QtImport.load_ui_file("esrf_sample_centering.ui")

        # Size policy --------------------------------
        self.ui_widgets_manager.aligment_table.setSizePolicy(
            QtImport.QSizePolicy.Minimum,
            QtImport.QSizePolicy.Minimum,
        )

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout()
        _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        # MatPlotWidget --------------------------------------------------------------
         # a figure instance to plot on
        self.figure = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        _matplotlib_widget_layout = QtImport.QVBoxLayout()
        _matplotlib_widget_layout.addWidget(self.toolbar)
        _matplotlib_widget_layout.addWidget(self.canvas)
        
        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QHBoxLayout()
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.addLayout(_matplotlib_widget_layout)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
       
        self.ui_widgets_manager.show_center_checkbox.stateChanged.connect(
            self.show_center
        )

        self.ui_widgets_manager.show_help_line_checkbox.stateChanged.connect(
            self.show_help_lines
        )
        
        self.ui_widgets_manager.number_points_spinbox.valueChanged.connect(
            self.change_point_number
        )

        self.ui_widgets_manager.delta_phi_textbox.editingFinished.connect(
            self.delta_phi_changed
        )

        self.ui_widgets_manager.start_alignment_button.clicked.connect(
            self.start_centring
        )

        self.ui_widgets_manager.cancel_alignment_button.clicked.connect(
            self.cancel_centring
        )

        # TODO : add show center and show help line functionalities
        self.ui_widgets_manager.show_center_checkbox.hide()
        self.ui_widgets_manager.show_help_line_checkbox.hide()
        
        # Other ---------------------------------------------------------------

        self.plot_data_X = []
        self.plot_data_Y = []
        self.connect(HWR.beamline.sample_view, "centringStarted", self.centring_started)
        self.connect(HWR.beamline.sample_view, "centringFailed", self.centring_failed)
        self.connect(
            HWR.beamline.sample_view, "centringSuccessful", self.centring_successful
        )
        self.connect(HWR.beamline.diffractometer, "centring_image_clicked", self.image_clicked)
        self.connect(HWR.beamline.diffractometer, "centring_calculation_ended", self.show_centring_paremeters)

        self.change_point_number(self.points_for_aligment)

        # init delta_phi var value
        self.delta_phi_changed()

        # match default values in .ui file
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        self.delta_phi = float(self.ui_widgets_manager.delta_phi_textbox.text())

    def centring_started(self):
        """
        Used to clean the table from precedent data
        """
        #clean point table
        self.clean_table()
        self.num_clicked_centring_pos = 0
        self.ui_widgets_manager.number_points_spinbox.setEnabled(False)

    def centring_failed(self, method, centring_status):
        """
        Used to give feedback to user: table cells' background to red
        """
        table = self.ui_widgets_manager.aligment_table
        table.setRowCount(self.points_for_aligment)
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                table.item(row, column).setBackground(QtImport.QColor(QtImport.Qt.red))
        self.ui_widgets_manager.number_points_spinbox.setEnabled(True)

    def centring_successful(self):
        """
        Used to give feedback to user: table cells' background to green
        """
        table = self.ui_widgets_manager.aligment_table
        table.setRowCount(self.points_for_aligment)
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                table.item(row, column).setBackground(QtImport.QColor(QtImport.Qt.green))
        self.ui_widgets_manager.number_points_spinbox.setEnabled(True)

    def image_clicked(self, x, y):
        """
        Used to give feedback to user: update table's and plot's data
        """
        table = self.ui_widgets_manager.aligment_table
        self.plot_data_Y.append(x)
        self.plot_data_X.append(math.radians(self.delta_phi) * self.num_clicked_centring_pos)
        table.item(self.num_clicked_centring_pos, 1).setText(str(x))
        table.item(self.num_clicked_centring_pos, 2).setText(str(y))
        table.item(self.num_clicked_centring_pos, 0).setText(str(self.delta_phi * self.num_clicked_centring_pos))

        self.num_clicked_centring_pos += 1
 
        # instead of ax.hold(False)
        self.figure.clear()
        # plot data
        ax = self.figure.add_subplot()
        ax.plot(self.plot_data_X, self.plot_data_Y, 'ro')
        self.canvas.draw()

    def show_centring_paremeters(self, parameter_dict):
        """
        Used to give feedback to user: update plot's data
        """
        # use sample_centring module
        sample_centring.
        # from multipointcenter
        # p[0] * numpy.sin(x + p[1]) + p[2]
        amplitude = parameter_dict['r']
        phase = parameter_dict['alpha']
        offset = parameter_dict['offset']
        d_horizontal = parameter_dict['d_horizontal']
        phi_positions = parameter_dict['phi_positions']
        image_width_pix = HWR.beamline.sample_view.get_image_size()[0]
        beam_position_x = HWR.beamline.beam.get_beam_position_on_screen()[0]
        pixels_per_mm_hor = parameter_dict['pixelsPerMm_Hor']
        
        
        x_angle = numpy.linspace(phi_positions[0], 2 *numpy.pi + phi_positions[0], 360)
        sinus_signal = amplitude * numpy.sin(x_angle + phase) + offset
        
        # clear data
        self.figure.clear()
        # plot data
        ax = self.figure.add_subplot(121)
        ax.plot(x_angle, sinus_signal)
        ax.plot(
            numpy.array(phi_positions),
            numpy.array(self.plot_data_Y) / float(pixels_per_mm_hor), 'ro'
        )
        ax.axhspan(0, float(image_width_pix / pixels_per_mm_hor), facecolor='y', alpha=0.5)
        ax.axhline(y=float(beam_position_x / pixels_per_mm_hor), color='r', linestyle='-.')

        ax.axhspan(d_horizontal, d_horizontal + float(image_width_pix / pixels_per_mm_hor), facecolor='g', alpha=0.5)
        ax.axhline(y=d_horizontal + float(beam_position_x / pixels_per_mm_hor), color='b', linestyle='-.')

        ax2 = self.figure.add_subplot(122)
        ax2.plot(sinus_signal, x_angle)
        ax2.plot(
            numpy.array(self.plot_data_Y) / float(pixels_per_mm_hor), 'ro',
            numpy.array(phi_positions)            
        )
        ax2.axvspan(0, float(image_width_pix / pixels_per_mm_hor), facecolor='y', alpha=0.5)
        ax2.axvline(x=float(beam_position_x / pixels_per_mm_hor), color='r', linestyle='-.')

        ax2.axvspan(d_horizontal, d_horizontal + float(image_width_pix / pixels_per_mm_hor), facecolor='g', alpha=0.5)
        ax2.axvline(x=d_horizontal + float(beam_position_x / pixels_per_mm_hor), color='b', linestyle='-.')

        self.canvas.draw()

    def show_center(self, checkbox_state):
        """
        Doc
        TODO: Heritated from Framework2.
        To be developped if needed
        """
        pass
    def show_help_lines(self, checkbox_state):
        """
        Doc
        TODO: Heritated from Framework2.
        To be developped if needed
        """
        pass
    def start_centring(self):
        """
        Launch aligment process
        """
        HWR.beamline.sample_view.start_centring(tree_click=True)
    def cancel_centring(self):
        """
        Cancel aligment process
        """
        self.plot_data_X.clear()
        self.plot_data_Y.clear()
        self.figure.clear()
        HWR.beamline.sample_view.reject_centring()

    def change_point_number(self, new_int_value):
        """
        Adapt
        """
        self.points_for_aligment = new_int_value

        # restart the table and populate with items
        table = self.ui_widgets_manager.aligment_table
        table.clearContents()
        table.setRowCount(self.points_for_aligment)

        for row in range(table.rowCount()):
            table.setItem(row, 0, QtImport.QTableWidgetItem(""))
            table.setItem(row, 1, QtImport.QTableWidgetItem(""))
            table.setItem(row, 2, QtImport.QTableWidgetItem(""))
        
        if HWR.beamline.diffractometer is not None:
            HWR.beamline.diffractometer.set_centring_parameters(
                self.points_for_aligment,
                self.delta_phi
            )

        #self.emit_centring_parameters_changed()

    def delta_phi_changed(self):
        delta_phi_str = self.ui_widgets_manager.delta_phi_textbox.text()
        try:
            self.delta_phi = float(delta_phi_str.replace(" ", ""))
        except ValueError as error:
            logging.getLogger().error(
                f"""Sorry, could not transform {delta_phi_str} into a float var.
                Using default {self.delta_phi} value"""
            )
        
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        if HWR.beamline.diffractometer is not None:
            HWR.beamline.diffractometer.set_centring_parameters(
                self.points_for_aligment,
                self.delta_phi
            )
        
    def clean_table(self):
        """
        Adapt
        """
        table = self.ui_widgets_manager.aligment_table
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        table.setRowCount(self.points_for_aligment)
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                table.item(row, column).setText("")
                table.item(row, column).setData(QtImport.Qt.BackgroundRole, None)
            