#! /usr/bin/env python
# encoding: utf-8
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

"""GPhL bespoke input widget. Built from DataCollectParametersWidget"""

import logging
from collections import namedtuple
from collections import OrderedDict

from gui.utils import QtImport
from gui.utils.widget_utils import DataModelInputBinder

from HardwareRepository.HardwareObjects import queue_model_enumerables
from HardwareRepository.dispatcher import dispatcher

__category__ = "TaskToolbox_Tabs"

__copyright__ = """ Copyright © 2016 - 2019 by Global Phasing Ltd. """
__license__ = "LGPLv3+"
__author__ = "Rasmus H Fogh"

CrystalSystemData = namedtuple("CrystalSystemData", ("crystal_system", "point_groups"))
CrystalData = namedtuple(
    "CrystalData", ("name", "space_group", "a", "b", "c", "alpha", "beta", "gamma")
)


class GphlAcquisitionData(object):
    """Dummy container class for global phasing acquisition data

    Attributes are set in the GphlAcquisitionWidget"""

    pass


class GphlSetupWidget(QtImport.QWidget):
    """Superclass for GPhL interface widgets"""

    def __init__(self, parent=None, name="gphl_setup_widget"):
        QtImport.QWidget.__init__(self, parent)
        if name is not None:
            self.setObjectName(name)

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        dispatcher.connect(self._refresh_interface, "model_update", dispatcher.Any)

        # Hardware objects ----------------------------------------------------

        # Internal variables -------------------------------------------------
        self._widget_data = OrderedDict()
        self._data_object = GphlAcquisitionData()
        self._pulldowns = {}
        self._parameter_mib = DataModelInputBinder(self._data_object)

        # Graphic elements ----------------------------------------------------
        _parameters_widget = self._parameters_widget = QtImport.QWidget(self)
        QtImport.QGridLayout(_parameters_widget)
        _parameters_widget.layout().setColumnStretch(2, 1)

        # Layout --------------------------------------------------------------
        # This seems to be necessary to make widget visible
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(_parameters_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def setEnabled(self, value):
        super(GphlSetupWidget, self).setEnabled(value)
        for tag in self._widget_data:
            self.set_parameter_enabled(tag, value, warn=False)

    def set_parameter_enabled(self, tag, value, warn=True):
        tt = self._widget_data.get(tag)
        if tt:
            if hasattr(tt[0], "setEnabled"):
                tt[0].setEnabled(value)
            elif warn:
                logging.getLogger().warning(
                    "%s Widget has no attribute setEnabled" % tag
                )
        elif warn:
            logging.getLogger().warning("%s field not found in GphlSetupWidget" % tag)

    def get_data_object(self):
        return self._data_object

    def populate_widget(self, **kw):

        self._data_object = data_object = GphlAcquisitionData()
        self._parameter_mib.bindings.clear()
        # NB must be done here to set empty model, and also in subclasses:
        self._parameter_mib.set_model(data_object)
        for field_name, tags in self._pulldowns.items():
            widget = self._widget_data[field_name][0]
            widget.clear()
            widget.addItems(list(QtImport.QString(tag) for tag in tags))
            widget.setCurrentIndex(0)

    def set_parameter_value(self, name, value):
        """Set value - NB ComboBoxes are set by text, not index"""
        if hasattr(self._data_object, name):
            tags = self._pulldowns.get(name)
            if tags is None:
                # Not a pulldown
                setattr(self._data_object, name, value)
            else:
                # This is a pulldown
                if value in tags:
                    indx = tags.index(value)
                    setattr(self._data_object, name, indx)

                else:
                    raise ValueError(
                        "GPhL acquisition widget %s pulldown has no value %s"
                        % (name, value)
                    )

            self._parameter_mib._update_widget(name, None)
        else:
            raise ValueError("GPhL acquisition widget has no parameter named %s" % name)

    def get_parameter_value(self, name):
        """Return value of parameter <name> or None if it does not exist

        NB ComboBoxes return text values, not indices

        NB, the attributes defined on the _data_object depend on context,
        so it is practical not to get errors for unknown names """
        if hasattr(self._data_object, name):
            tags = self._pulldowns.get(name)
            if tags is None:
                # Not a pulldown
                return getattr(self._data_object, name)
            else:
                # This is a pulldown - get text from index
                return tags[getattr(self._data_object, name)]
        else:
            return None

    def _get_label_name(self, name):
        return name + "_label"

    def _refresh_interface(self, field_name, data_binder):
        """Refresh interface when values change"""
        pass


class GphlDiffractcalWidget(GphlSetupWidget):
    """Input widget for GPhL diffractometer calibration setup"""

    def __init__(
        self, parent=None, name="gphl_acquisition_widget", workflow_object=None
    ):
        GphlSetupWidget.__init__(self, parent=parent, name=name)

        _parameters_widget = self._parameters_widget

        # Internal variables -------------------------------------------------

        # Get test crystal data
        self.test_crystals = OrderedDict()
        xx = next(workflow_object.getObjects("test_crystals"))
        for test_crystal in xx.getObjects("test_crystal"):
            dd = test_crystal.getProperties()
            self.test_crystals[dd["name"]] = CrystalData(**dd)

        row = 0
        field_name = "test_crystal"
        label_name = self._get_label_name(field_name)
        label_str = "Test Crystal :"
        label = QtImport.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = QtImport.QComboBox()
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (widget, str, None, 0)
        self._pulldowns[field_name] = list(self.test_crystals)

        row += 1
        label_name = "test_crystal_spacegroup"
        label_str = " "
        label = QtImport.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        label_name = "test_crystal_parameters"
        label_str = " "
        label = QtImport.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 1)
        self._widget_data[label_name] = (label, str, None, label_str)

    def populate_widget(self, **kw):
        GphlSetupWidget.populate_widget(self, **kw)

        data_object = self._data_object

        for tag, tt in self._widget_data.items():
            widget, w_type, validator, value = tt
            widget.show()

            if tag in kw:
                value = kw[tag]
            setattr(data_object, tag, value)
            self._parameter_mib.bind_value_update(tag, widget, w_type, validator)
        # Must be redone here, after values and bindings are set
        self._parameter_mib.set_model(data_object)

        # Special case, reset space_group pulldown
        # which changes with crystal_system
        self._refresh_interface("test_crystal", None)

    def _refresh_interface(self, field_name, data_binder):
        """Refresh interface when values change"""
        if field_name == "test_crystal":
            # Refresh crystal parameters label to reflect test_crystal pulldown
            test_crystal = self.get_parameter_value("test_crystal") or ""
            crystal_data = self.test_crystals.get(test_crystal)
            if crystal_data:
                label_str1 = "Spacegroup=%(space_group)s\n\n" % crystal_data._asdict()
                label_str2 = (
                    "a=%(a)s   b=%(b)s   c=%(c)s\n"
                    + "alpha=%(alpha)s   beta=%(beta)s   gamma=%(gamma)s\n"
                ) % crystal_data._asdict()
            else:
                label_str1 = label_str2 = " "
            label = self._widget_data["test_crystal_spacegroup"][0]
            label.setText(QtImport.QString(label_str1))

            label = self._widget_data["test_crystal_parameters"][0]
            label.setText(QtImport.QString(label_str2))


class GphlAcquisitionWidget(GphlSetupWidget):
    """Input widget for GPhL data collection setup"""

    # Popup label to point groups dict
    _CRYSTAL_SYSTEM_DATA = OrderedDict(
        (
            ("", CrystalSystemData("", (None,))),
            ("Triclinic    |   1", CrystalSystemData("Triclinic", ("1",))),
            ("Monoclinic   |   2", CrystalSystemData("Monoclinic", ("2",))),
            ("Orthorhombic | 222", CrystalSystemData("Orthorhombic", ("222",))),
            ("Tetragonal   | Any", CrystalSystemData("Tetragonal", ("4", "422"))),
            ("Tetragonal   |   4", CrystalSystemData("Tetragonal", ("4",))),
            ("Tetragonal   | 422", CrystalSystemData("Tetragonal", ("422",))),
            (
                "Trigonal     | Any",
                CrystalSystemData("Trigonal", ("3", "32", "321", "312")),
            ),
            ("Trigonal     |   3", CrystalSystemData("Trigonal", ("3",))),
            ("Trigonal     |  32", CrystalSystemData("Trigonal", ("32", "321", "312"))),
            ("Hexagonal    | Any", CrystalSystemData("Hexagonal", ("6", "622"))),
            ("Hexagonal    |   6", CrystalSystemData("Hexagonal", ("6",))),
            ("Hexagonal    | 622", CrystalSystemData("Hexagonal", ("622",))),
            ("Cubic        | Any", CrystalSystemData("Cubic", ("23", "432"))),
            ("Cubic        |  23", CrystalSystemData("Cubic", ("23",))),
            ("Cubic        | 432", CrystalSystemData("Cubic", ("432",))),
        )
    )

    def __init__(self, parent=None, name="gphl_acquisition_widget"):
        GphlSetupWidget.__init__(self, parent=parent, name=name)

        # Internal variables -------------------------------------------------

        _parameters_widget = self._parameters_widget

        row = 0
        field_name = "crystal_system"
        label_name = self._get_label_name(field_name)
        label_str = "Crystal system :"
        label = QtImport.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = QtImport.QComboBox()
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (widget, str, None, 0)
        self._pulldowns[field_name] = list(self._CRYSTAL_SYSTEM_DATA)

        row += 1
        field_name = "space_group"
        label_name = self._get_label_name(field_name)
        label_str = "Space group :"
        label = QtImport.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = QtImport.QComboBox()
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (widget, str, None, 0)

    def populate_widget(self, **kw):
        GphlSetupWidget.populate_widget(self, **kw)

        data_object = self._data_object

        # Special case, reset space_group pulldown
        # which changes with crystal_system
        self._refresh_interface("crystal_system", None)

        skip_fields = []

        for tag, tt in self._widget_data.items():
            if tag in skip_fields:
                tt[0].hide()
            else:
                widget, w_type, validator, value = tt
                widget.show()

                if tag in kw:
                    value = kw[tag]
                setattr(data_object, tag, value)
                self._parameter_mib.bind_value_update(tag, widget, w_type, validator)

        # Must be redone here, after values and bindings are set
        self._parameter_mib.set_model(data_object)

    def _refresh_interface(self, field_name, data_binder):
        """Refresh interface when values change"""
        if field_name == "crystal_system":
            # Refresh space_group pulldown to reflect crystal_system pulldown
            crystal_system = self.get_parameter_value("crystal_system") or ""
            data = self._CRYSTAL_SYSTEM_DATA[crystal_system]
            ll = self._pulldowns["space_group"] = []
            if data.crystal_system:
                ll.append("")
                ll.extend(
                    [
                        x.name
                        for x in queue_model_enumerables.SPACEGROUP_DATA
                        if x.point_group in data.point_groups
                    ]
                )
            else:
                ll.extend(queue_model_enumerables.XTAL_SPACEGROUPS)

            widget = self._widget_data["space_group"][0]
            widget.clear()
            widget.addItems(list(QtImport.QString(tag) for tag in ll))
            self._data_object.space_group = 0
            # widget.setCurrentIndex(0)
            # self._parameter_mib._update_widget('space_group', None)
