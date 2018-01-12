"""GPhL bespoke input widget. Built from DataCollectParametersWidget"""

import logging

from PyQt4 import QtCore
from PyQt4 import QtGui
from widgets.Qt4_widget_utils import DataModelInputBinder

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

__category__ = 'Qt4_TaskToolbox_Tabs'

class GphlAcquisitionData(object):
    """Dummy container class for global phasing acquisition data

    Attributes are set in the GphlAcquisitionWidget"""
    pass

class GphlAcquisitionWidget(QtGui.QWidget):

    def __init__(self, parent=None, name='gphl_acquisition_widget'):
        QtGui.QWidget.__init__(self,parent)
        if name is not None:
            self.setObjectName(name)

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------

         # Internal variables -------------------------------------------------
        self.beam_energy_tags = ()
        self._widget_data = OrderedDict()
        self._data_object = GphlAcquisitionData()

        # Graphic elements ----------------------------------------------------
        _parameters_widget = QtGui.QWidget(self)
        QtGui.QGridLayout(_parameters_widget)
        _parameters_widget.layout().setColumnStretch(2, 1)

        # Layout --------------------------------------------------------------
        # This seems to be necessary to make widget visible
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(_parameters_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        row = 0
        field_name = 'expected_resolution'
        label_name = self._get_label_name(field_name)
        label_str = "Expected resolution (A) :"
        label=QtGui.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = QtGui.QLineEdit()
        widget.setAlignment(QtCore.Qt.AlignLeft)
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (
            widget, float, QtGui.QDoubleValidator(0.01, 20, 2, self), 0.0
        )

        row += 1
        label_name = 'beam_energies_label'
        label_str = "Beam energies (keV):"
        label=QtGui.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)

        self.beam_energy_tags = ('energy_1', 'energy_2', 'energy_3',
                                 'energy_4',)

        ii = 0
        for label_str in ("First beam energy", "Second beam energy",
                          "Third beam energy", "Fourth beam energy"):
            ii += 1
            row += 1
            field_name = 'energy_%s' % ii
            label_name = self._get_label_name(field_name)
            label=QtGui.QLabel(label_str, _parameters_widget)
            _parameters_widget.layout().addWidget(label, row, 0)
            self._widget_data[label_name] = (label, str, None, label_str)
            widget = QtGui.QLineEdit()
            widget.setAlignment(QtCore.Qt.AlignLeft)
            _parameters_widget.layout().addWidget(widget, row, 1)
            self._widget_data[field_name] = (
                widget, float, QtGui.QDoubleValidator(0.01, 200, 2, self), 0.0
            )

    def setEnabled(self, value):
        super(GphlAcquisitionWidget, self).setEnabled(value)
        for tag in self._widget_data:
            self.set_parameter_enabled(tag, value, warn=False)

    def set_parameter_enabled(self, tag, value, warn=True):
        tt = self._widget_data.get(tag)
        if tt:
            if hasattr(tt[0], 'setEnabled'):
                tt[0].setEnabled(value)
            elif warn:
                logging.getLogger().warning(
                    "%s Widget has no attribute setEnabled" % tag
                )
        elif warn:
            logging.getLogger().warning(
                "%s field not found in GphlAcquisitinoWidget" % tag
            )

    def get_data_object(self):
        return self._data_object

    def populate_widget(self, beam_energies={}, **kw):

        data_object = self._data_object = GphlAcquisitionData()
        parameter_mib = self._parameter_mib = DataModelInputBinder(data_object)
        widget_data = self._widget_data

        skip_fields = []
        for tag in self.beam_energy_tags[len(beam_energies):]:
            skip_fields.append(tag)
            skip_fields.append(self._get_label_name(tag))
        if not beam_energies:
            skip_fields.append('beam_energies_label')

        for tag, tt in widget_data.items():
            if tag in skip_fields:
                tt[0].hide()
            else:
                widget, w_type, validator, value = tt
                widget.show()

                if tag in kw:
                    value = kw[tag]
                elif tag in self.beam_energy_tags:
                    ii = self.beam_energy_tags.index(tag)
                    if ii < len(beam_energies):
                        name = list(beam_energies)[ii]
                        value = beam_energies[name]
                        label_tag = self._get_label_name(tag)
                        setattr(data_object, label_tag, name)

                setattr(data_object, tag, value)
                parameter_mib.bind_value_update(tag, widget, w_type, validator)

        parameter_mib.init_bindings()

    def get_energy_dict(self):
        """get role:value dict for energies"""
        result = OrderedDict()
        for tag in self.beam_energy_tags:
            if hasattr(self._data_object, tag):
                role = getattr(self._data_object, self._get_label_name(tag))
                result[role] = getattr(self._data_object, tag)
        #
        return result

    def set_parameter_value(self, name, value):
        if hasattr(self._data_object, name):
            setattr(self._data_object, name, value)
            self._parameter_mib._update_widget(name, None)
        else:
            raise ValueError(
                "GPhL acquisition widget has no parameter named %s" % name
            )

    def _get_label_name(self, name):
        return name + '_label'
