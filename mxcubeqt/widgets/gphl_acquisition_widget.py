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
from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

import logging
from collections import namedtuple
from collections import OrderedDict

from mxcubeqt.utils import qt_import
from mxcubeqt.utils.widget_utils import DataModelInputBinder
from mxcubeqt.utils.paramsgui import make_widget

from mxcubecore.HardwareObjects import queue_model_enumerables
from mxcubecore.dispatcher import dispatcher

from mxcubecore import HardwareRepository as HWR

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


class GphlSetupWidget(qt_import.QWidget):
    """Superclass for GPhL interface widgets"""

    def __init__(self, parent=None, name="gphl_setup_widget"):
        qt_import.QWidget.__init__(self, parent)
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
        self._pulldown_defaults = {}
        self._parameter_mib = DataModelInputBinder(self._data_object)

        # Graphic elements ----------------------------------------------------
        _parameters_widget = self._parameters_widget = qt_import.QWidget(self)
        qt_import.QGridLayout(_parameters_widget)
        _parameters_widget.layout().setColumnStretch(2, 1)
        # _parameters_widget.layout().setMargin(0)
        _parameters_widget.layout().setSpacing(0)
        # _parameters_widget.layout().setContentsMargins(0, 0, 0, 0)

        # Layout --------------------------------------------------------------
        # This seems to be necessary to make widget visible
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(_parameters_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def setEnabled(self, value):
        super(GphlSetupWidget, self).setEnabled(value)
        for tag in self._widget_data:
            self.set_parameter_enabled(tag, value, warn=False)

    def set_parameter_enabled(self, tag, value, warn=True):
        tt0 = self._widget_data.get(tag)
        if tt0:
            if hasattr(tt0[0], "setEnabled"):
                tt0[0].setEnabled(value)
            elif warn:
                logging.getLogger().warning(
                    "%s Widget has no attribute setEnabled" % tag
                )
        elif warn:
            logging.getLogger().warning("%s field not found in GphlSetupWidget" % tag)

    def get_data_object(self):
        return self._data_object

    def populate_widget(self, **kwargs):

        self._data_object = data_object = GphlAcquisitionData()
        self._parameter_mib.bindings.clear()
        # NB must be done here to set empty model, and also in subclasses:
        self._parameter_mib.set_model(data_object)
        for field_name, tags in self._pulldowns.items():
            widget = self._widget_data[field_name][0]
            widget.clear()
            widget.addItems(list(qt_import.QString(tag) for tag in tags))
            default_label = self._pulldown_defaults.get(field_name)
            if default_label is None:
                widget.setCurrentIndex(0)
                self._data_object.space_group = 0

            else:
                widget.setCurrentIndex(widget.findText(default_label))

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

    def __init__(self, parent=None, name="gphl_diffractcal_widget"):
        GphlSetupWidget.__init__(self, parent=parent, name=name)

        _parameters_widget = self._parameters_widget

        # Internal variables -------------------------------------------------

        # Get test crystal data
        self.test_crystals = OrderedDict(HWR.beamline.gphl_workflow.test_crystals)
        # xx0 = next(HWR.beamline.gphl_workflow.get_objects("test_crystals"))
        # for test_crystal in xx0.get_objects("test_crystal"):
        #     dd0 = test_crystal.get_properties()
        #     self.test_crystals[dd0["name"]] = CrystalData(**dd0)

        row = 0
        field_name = "test_crystal"
        label_name = self._get_label_name(field_name)
        label_str = "Test Crystal :"
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = qt_import.QComboBox()
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (widget, str, None, 0)
        self._pulldowns[field_name] = list(self.test_crystals)

        row += 1
        label_name = "test_crystal_spacegroup"
        label_str = " "
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        label_name = "test_crystal_parameters"
        label_str = " "
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 1)
        self._widget_data[label_name] = (label, str, None, label_str)

        row += 1
        field_name = "relative_rad_sensitivity"
        label_name = self._get_label_name(field_name)
        label_str = "Rel. radiation sensitivity"
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = qt_import.QLineEdit()
        _parameters_widget.layout().addWidget(widget, row, 1)
        validator = qt_import.QDoubleValidator(0, 100, 4, widget)
        self._widget_data[field_name] = (widget, float, validator, 1.0)

    def populate_widget(self, **kwargs):
        GphlSetupWidget.populate_widget(self, **kwargs)

        data_object = self._data_object

        for tag, tt0 in self._widget_data.items():
            widget, w_type, validator, value = tt0
            widget.show()

            if tag in kwargs:
                value = kwargs[tag]
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
            label.setText(qt_import.QString(label_str1))

            label = self._widget_data["test_crystal_parameters"][0]
            label.setText(qt_import.QString(label_str2))

class GphlRuntimeWidget(qt_import.QWidget):
    def __init__(self, parent, name="gphl_runtime_widget", data_object=None):
        qt_import.QWidget.__init__(self, parent)
        if name is not None:
            self.setObjectName(name)

        self._data_object = data_object

        # Internal variables -------------------------------------------------


        # Graphic elements ----------------------------------------------------
        _parameters_widget = self._parameters_widget = qt_import.QWidget(self)
        qt_import.QGridLayout(_parameters_widget)
        _parameters_widget.layout().setColumnStretch(2, 1)
        # _parameters_widget.layout().setMargin(0)
        _parameters_widget.layout().setSpacing(0)
        # _parameters_widget.layout().setContentsMargins(0, 0, 0, 0)

        # Layout --------------------------------------------------------------
        # This seems to be necessary to make widget visible
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(_parameters_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        # _main_vlayout.addStretch(0)
        # _main_vlayout.setSpacing(6)
        # _main_vlayout.setContentsMargins(2, 2, 2, 2)

        if data_object is not None:
            self.populate_widget(data_object)

        self._fields = OrderedDict(
            (
                (
                    "dose_budget",
                     {
                        "label": "Total dose budget (MGy)",
                        "getter": "get_dose_budget",
                         "options":{
                            "variableName":"dose_consumed",
                             "decimals":2,
                             "type":"floatstring",
                             "readOnly":True,
                         }
                     }
                ),
                (
                    "dose_consumed",
                    {
                        "label": "Acq. dose budget (MGy)",
                        "getter": "get_dose_consumed",
                        "options":{
                            "variableName":"dose_consumed",
                            "decimals":2,
                            "type":"floatstring",
                            "readOnly":True,
                        }
                    }
                ),
                (
                    "exposure_time",
                    {
                        "label": "Exposure tiume (s)",
                        "getter": "get_exposure_time",
                        "options":{
                            "variableName":"exposure_time",
                            "decimals":4,
                            "type":"floatstring",
                            "readOnly":True,
                        }
                    }
                ),
                (
                    "image_width",
                    {
                        "label": "Oscillation range",
                        "getter": "get_image_width",
                        "options":{
                            "variableName":"image_width",
                            "decimals":2,
                            "type":"floatstring",
                            "readOnly":True,
                        }
                    }
                ),
            )
        )

        row = 0
        for tag,dd0 in self._fields.items():
            label = qt_import.QLabel(dd0["label"], _parameters_widget)
            _parameters_widget.layout().addWidget(
                label, row, 0, qt_import.Qt.AlignLeft
            )
            widget = make_widget(_parameters_widget, dd0["options"])
            _parameters_widget.layout().addWidget(
                widget, row, 1, qt_import.Qt.AlignLeft
            )
            dd0["widget"] = widget
            row += 1

    def populate_widget(self, data_object, **kwargs):

        self._data_object = data_object

        for tag, dd0 in self._fields.items():
            value = getattr(data_object, dd0["getter"])() or 0
            dd0["widget"].set_value(value)



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
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = qt_import.QComboBox()
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (widget, str, None, 0)
        self._pulldowns[field_name] = list(self._CRYSTAL_SYSTEM_DATA)

        row += 1
        field_name = "space_group"
        label_name = self._get_label_name(field_name)
        label_str = "Space group :"
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = qt_import.QComboBox()
        _parameters_widget.layout().addWidget(widget, row, 1)
        self._widget_data[field_name] = (widget, str, None, 0)

        row += 1
        field_name = "relative_rad_sensitivity"
        label_name = self._get_label_name(field_name)
        label_str = "Rel. radiation sensitivity"
        label = qt_import.QLabel(label_str, _parameters_widget)
        _parameters_widget.layout().addWidget(label, row, 0)
        self._widget_data[label_name] = (label, str, None, label_str)
        widget = qt_import.QLineEdit()
        _parameters_widget.layout().addWidget(widget, row, 1)
        validator = qt_import.QDoubleValidator(0, 100, 4, widget)
        self._widget_data[field_name] = (widget, float, validator, 1.0)
        if HWR.beamline.gphl_workflow.settings.get("advanced_mode"):
            # ADVANCED - not currently used
            row += 1
            field_name = "characterisation_strategy"
            label_name = self._get_label_name(field_name)
            label_str = "Characterisation strategy :"
            label = qt_import.QLabel(label_str, _parameters_widget)
            _parameters_widget.layout().addWidget(label, row, 0)
            self._widget_data[label_name] = (label, str, None, label_str)
            widget = qt_import.QComboBox()
            _parameters_widget.layout().addWidget(widget, row, 1)
            self._widget_data[field_name] = (widget, str, None, 0)
            strategy_names = (
                HWR.beamline.gphl_workflow.settings["characterisation_strategies"]
            )
            self._pulldowns[field_name] = strategy_names

            #
            row += 1
            field_name = "use_for_indexing"
            label_name = self._get_label_name(field_name)
            label_str = "Use input cell for indexing?"
            label = qt_import.QLabel(label_str, _parameters_widget)
            _parameters_widget.layout().addWidget(label, row, 0)
            self._widget_data[label_name] = (label, str, None, label_str)
            widget = qt_import.QCheckBox()
            _parameters_widget.layout().addWidget(widget, row, 1)
            self._widget_data[field_name] = (widget, bool, None, False)

            row += 1
            field_name = "decay_limit"
            label_name = self._get_label_name(field_name)
            label_str = "Signal decay limit (%)"
            label = qt_import.QLabel(label_str, _parameters_widget)
            _parameters_widget.layout().addWidget(label, row, 0)
            self._widget_data[label_name] = (label, str, None, label_str)
            widget = qt_import.QLineEdit()
            widget.setReadOnly(True)
            widget.setEnabled(False)
            _parameters_widget.layout().addWidget(widget, row, 1)
            validator = qt_import.QDoubleValidator(0, 100, 4, widget)
            self._widget_data[field_name] = (
                widget,
                float,
                validator,
                HWR.beamline.gphl_workflow.settings["defaults"].get("decay_limit", 25)
            )

    def populate_widget(self, **kwargs):
        GphlSetupWidget.populate_widget(self, **kwargs)

        data_object = self._data_object

        # Special case, reset space_group pulldown
        # which changes with crystal_system
        self._refresh_interface("crystal_system", None)

        skip_fields = []

        for tag, tt0 in self._widget_data.items():
            if tag in skip_fields:
                tt0[0].hide()
            else:
                widget, w_type, validator, value = tt0
                widget.show()

                if tag in kwargs:
                    value = kwargs[tag]
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
            ll0 = self._pulldowns["space_group"] = []
            if data.crystal_system:
                ll0.append("")
                ll0.extend(
                    [
                        x.name
                        for x in queue_model_enumerables.SPACEGROUP_DATA
                        if x.point_group in data.point_groups
                    ]
                )
            else:
                ll0.extend(queue_model_enumerables.XTAL_SPACEGROUPS)

            widget = self._widget_data["space_group"][0]
            widget.clear()
            widget.addItems(list(qt_import.QString(tag) for tag in ll0))
            self._data_object.space_group = 0
            # widget.setCurrentIndex(0)
            # self._parameter_mib._update_widget('space_group', None)
