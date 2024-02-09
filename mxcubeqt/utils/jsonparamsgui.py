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


"""PyQt Schema-driven UI for runtime queries - port of paramsgui - rhfogh Jan 2018,
Refactored May 2023 to taek JSON schema as input
Refactored July 2024 to work with web version (update functions on server side)
"""
import abc
import os.path
import logging
from typing import Any, Optional, Dict, Sequence, List
import gevent
import gevent.event

from mxcubecore.dispatcher import dispatcher
from mxcubecore import HardwareRepository as HWR
from mxcubeqt.utils import qt_import, colors


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"

ColourMap = {
    "OK": colors.WHITE,
    "WARNING": colors.LIGHT_YELLOW,
    "ERROR": colors.LINE_EDIT_ERROR,
    "CHANGED": colors.LINE_EDIT_CHANGED,
    "HIGHLIGHT": colors.LIGHT_GREEN,
}


class LayoutWidget(qt_import.QWidget):
    """Collection-of-widgets widget for parameter query"""

    parametersValidSignal = qt_import.pyqtSignal(bool)

    def __init__(self, options: Dict[str, Any]):

        self.parameter_widgets: Dict[str, ValueWidget] = {}
        self.return_signal: str = options.get("return_signal")
        self.update_signal: str = options.get("update_signal")
        self.update_on_change: Optional[bool] = options.get("update_on_change")
        self.block_updates: bool = False
        qt_import.QWidget.__init__(self)
        if self.update_signal:
            dispatcher.connect(self.update_values, self.update_signal, dispatcher.Any)

        # event to handle waiting for parameter input
        self.wait_event: gevent.event.Event = gevent.event.Event()

    def close(self) -> None:
        """Close widget and disconnect signals"""
        super().close()
        if self.update_signal:
            dispatcher.disconnect(
                self.update_values, self.update_signal, dispatcher.Any
            )
        for widget in self.parameter_widgets.values():
            widget.close()

    def set_values(self, **values) -> None:
        """Set values for all fields from values dictionary"""
        for tag, val in values.items():
            self.parameter_widgets[tag].set_value(val)

    def get_values_map(self) -> Dict[str, Any]:
        """Get parameter values dictionary for all fields"""
        return dict(
            (tag, val.get_value()) for tag, val in self.parameter_widgets.items()
        )

    def update_values(self, changes_dict: Dict[str, dict]) -> None:
        """Apply GUI updates returned from server

        Input is a field_name: dict2 dictionary
        with dict2 having (optional) keys "
        value" (Any), "options"  (dict) and "highlight"
        """
        try:
            # Do not trigger further updates while executing these.
            self.block_updates = True
            for tag, ddict in changes_dict.items():
                widget: ValueWidget = self.parameter_widgets[tag]
                options: dict = ddict.get("options")
                if options is not None:
                    if hasattr(widget, "reset_options"):
                        widget.reset_options(options)
                    else:
                        raise ValueError(
                            " reset_options not supported for widget %s of type %s"
                            % (tag, widget.__class__.__name__)
                        )
                if "value" in ddict:
                    widget.set_value(ddict["value"])
                highlight: str = ddict.get("highlight")
                widget.highlight = highlight
        finally:
            self.block_updates = False
            self.wait_event.set()

    def validate_fields(self, editing: Optional[str] = None) -> None:
        """Validate fields, emit all_valid signal, and set widget colours"""
        all_valid: bool = True
        for field_name, widget in self.parameter_widgets.items():
            if widget.is_valid():
                highlight: str = widget.highlight
                if not highlight:
                    if field_name == editing:
                        highlight = "CHANGED"
                    else:
                        highlight = "OK"
            else:
                all_valid = False
                print(
                    "WARNING, invalid value %s for %s"
                    % (widget.get_value(), field_name)
                )
                highlight = "ERROR"
            widget.colour_widget(highlight)
        self.parametersValidSignal.emit(all_valid)


class ValueWidget(qt_import.QWidget):
    """Mixin class for widgets containg actual values (i..e not containers)"""

    def __init__(
        self,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        # NB QWidget.__init__ is called from subclasses, should NOT be called here
        self.is_hidden: bool = options.get("hidden")
        self.gui_root_widget: LayoutWidget = gui_root_widget
        self.__name: str = options["variable_name"]
        if "default" in options:
            self.set_value(options["default"])
        self.update_on_change: bool = bool(options.get("update_on_change"))
        self.highlight: Optional[str] = options.get("highlight")
        if self.is_hidden:
            self.hide()
            self.setEnabled(False)
        elif options.get("readOnly"):
            self.setEnabled(False)
        self.setContentsMargins(1, 1, 1, 1)

    @abc.abstractmethod
    def set_value(self, value: Any) -> None:
        """Set widget value."""

    def get_name(self) -> str:
        """Get field name"""
        return self.__name

    def is_valid(self) -> bool:
        """Default value. Override in subclasses, when there is validity checking"""
        return True

    def input_field_changed(self) -> None:
        """UI update function triggered by field value changes

        Sends root_widget.return_signal and waits for reply"""
        root_widget: LayoutWidget = self.gui_root_widget
        if root_widget.block_updates:
            return
        valid: bool = self.is_valid()
        if valid:
            update_on_change: Optional[str] = self.gui_root_widget.update_on_change
            if update_on_change and (
                self.update_on_change or update_on_change == "always"
            ):
                self.gui_root_widget.wait_event.clear()
                HWR.beamline.emit(
                    root_widget.return_signal,
                    self.get_name(),
                    root_widget.get_values_map(),
                )
                self.gui_root_widget.wait_event.wait()
        root_widget.validate_fields()
        if valid:
            self.colour_widget("CHANGED")

    def colour_widget(self, highlight: str) -> None:
        """Colour widget according to highlight string

        Args:
            highlight: A string key to the ColourMap mapping

        Returns: None

        """
        colour = ColourMap[highlight]
        # colors.set_widget_color(self, colour, qt_import.QPalette.Base)
        widget_palette: qt_import.QPalette = self.palette()
        widget_palette.setColor(qt_import.QPalette.Base, colour)
        self.setPalette(widget_palette)


class LineEdit(qt_import.QLineEdit, ValueWidget):
    """Standard LineEdit widget"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QLineEdit.__init__(self, parent)
        ValueWidget.__init__(self, gui_root_widget, options)
        self.setAlignment(qt_import.Qt.AlignRight)
        if options.get("readOnly"):
            self.setReadOnly(True)
        self.textEdited.connect(self.input_field_changed)

    def set_value(self, value: str) -> None:
        """Set widget value"""
        self.setText(value)

    def get_value(self) -> str:
        """Get widget value"""
        return str(self.text())

    def close(self):
        """Close widget and disconnect signals"""
        self.textEdited.disconnect(self.input_field_changed)


class FloatString(LineEdit):
    """LineEdit widget with validators and formatting for floating point numbers"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        decimals: int = options.get("decimals")
        if decimals is None:
            self.formatstr = "%s"
        else:
            self.formatstr = "%%.%sf" % decimals
        # NB __init__ call must be AFTER setting self.formatstr
        LineEdit.__init__(self, parent, gui_root_widget, options)
        self.validator: qt_import.QDoubleValidator = qt_import.QDoubleValidator(self)
        val: Optional[float] = options.get("minimum")
        if val is not None:
            self.validator.setBottom(val)
        val: Optional[float] = options.get("maximum")
        if val is not None:
            self.validator.setTop(val)

    def set_value(self, value: Optional[float]) -> None:
        """Setter for widget value"""
        if value is None:
            self.setText(" ")
        else:
            self.setText(self.formatstr % value)

    def get_value(self) -> Optional[float]:
        """Getter for widget value"""
        val = self.text().strip()
        return float(val) if val else None

    def is_valid(self) -> bool:
        """Check if current value is valid"""

        if (
            self.validator.validate(self.text(), 0)[0]
            != qt_import.QValidator.Acceptable
        ):
            return False
        return True


class TextEdit(qt_import.QTextEdit, ValueWidget):
    """Standard text edit widget (multiline text)"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QTextEdit.__init__(self, parent)
        ValueWidget.__init__(self, gui_root_widget, options)
        self.setAlignment(qt_import.Qt.AlignLeft)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.setSizeAdjustPolicy(qt_import.QAbstractScrollArea.AdjustToContents)
        self.setFont(qt_import.QFont("Courier"))
        if options.get("readOnly"):
            self.setReadOnly(True)
        self.textChanged.connect(self.input_field_changed)

    def set_value(self, value: str) -> None:
        """Setter for widget value"""
        self.setText(value)

    def get_value(self) -> str:
        """Getter for widget value"""
        return str(self.toPlainText())

    def close(self):
        """Close widget and disconnect signals"""
        self.textChanged.disconnect(self.input_field_changed)


class TextDisplay(qt_import.QLabel):
    is_hidden: bool = False

    def __init__(
        self,
        parent: qt_import.QWidget,
        options: Dict[str, Any],
    ):
        qt_import.QLabel.__init__(self, parent)
        self.setFont(qt_import.QFont("Courier"))
        self.setText(qt_import.QString(options["default"]))


class Combo(qt_import.QComboBox, ValueWidget):
    """Standard ComboBox (pulldown) widget"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QComboBox.__init__(self, parent)
        # NB pulldown must be set up before ValueWidget init
        self.setup_pulldown(**options)
        ValueWidget.__init__(self, gui_root_widget, options)
        self.currentIndexChanged.connect(self.input_field_changed)
        self.setSizeAdjustPolicy(qt_import.QComboBox.AdjustToContents)

    def setup_pulldown(self, **options) -> None:
        """Set up pulldown from empty state (also used in resetting)"""
        self.enum: List[str] = options["enum"]
        for val in self.enum:
            self.addItem(str(val))
        if "default" in options:
            default = options["default"]
            if default in self.enum:
                self.set_value(options["default"])
            else:
                print(
                    "WARNING, %s default value %s is not a valid option"
                    % (options["variable_name"], default)
                )
                self.set_value(self.enum[0])

    def set_value(self, value) -> None:
        """Setter for widget value"""
        indx = self.findText(value)
        if indx >= 0:
            self.setCurrentIndex(indx)
        else:
            try:
                # NB this error may happen during init before ValueWidget init is called
                namestr = self.get_name()
            except AttributeError:
                namestr = str(self)
            raise ValueError("Value %s not found in widget %s" % (value, namestr))

    def get_value(self) -> Any:
        """Getter for widget value"""
        return str(self.currentText())

    def reset_options(self, options: Dict[str, Any]):
        """Reset pulldown contents, value, and is_hidden"""
        # Supported options are: value_dict, hidden, and default
        supported: frozenset = frozenset(("hidden", "enum", "default"))
        disallowed: frozenset = frozenset(options).difference(supported)
        if disallowed:
            raise ValueError(
                "Disallowed reset options for widget %s: %s"
                % (self.get_name(), sorted(disallowed))
            )
        self.clear()
        self.setup_pulldown(**options)

    def close(self):
        """Close widget and disconnect signals"""
        self.currentIndexChanged.disconnect(self.input_field_changed)


class File(ValueWidget, qt_import.QWidget):
    """Standard file selection widget"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QWidget.__init__(self, parent)
        ValueWidget.__init__(self, gui_root_widget, options)

        # do not allow qt to stretch us vertically
        policy: qt_import.QSizePolicy = self.sizePolicy()
        policy.setVerticalPolicy(qt_import.QSizePolicy.Fixed)
        self.setSizePolicy(policy)

        qt_import.QHBoxLayout(self)
        self.filepath: qt_import.QLineEdit = qt_import.QLineEdit(self)
        self.filepath.setAlignment(qt_import.Qt.AlignLeft)
        self.open_dialog_btn: qt_import.QPushButton = qt_import.QPushButton("...", self)
        self.open_dialog_btn.clicked.connect(self.open_file_dialog)

        self.layout().addWidget(self.filepath)
        self.layout().addWidget(self.open_dialog_btn)

    def set_value(self, value: str) -> None:
        """Setter for widget value"""
        self.filepath.setText(value)

    def get_value(self) -> str:
        """Getter for widget value"""
        return str(self.filepath.text())

    def open_file_dialog(self) -> None:
        """Ope file selection dialogue"""
        start_path: str = os.path.dirname(str(self.filepath.text()))
        if not os.path.exists(start_path):
            start_path = ""
        # Some Qt type, not sure of the class name
        path = qt_import.QFileDialog(self).getOpenFileName(directory=start_path)
        if not path.isNull():
            self.filepath.setText(path)


class IntSpinBox(qt_import.QSpinBox, ValueWidget):
    """Standard integer (spinbox) widget"""

    # CHANGED_COLOR = qt_import.QColor(255, 165, 0)

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QSpinBox.__init__(self, parent)
        ValueWidget.__init__(self, gui_root_widget, options)
        self.lineEdit().setAlignment(qt_import.Qt.AlignLeft)
        if "unit" in options:
            self.setSuffix(" " + options["unit"])
        if "default" in options:
            val: int = int(options["default"])
            self.setValue(val)
        if "maximum" in options:
            self.setMaximum(int(options["maximum"]))
        if "minimum" in options:
            self.setMinimum(int(options["minimum"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])
        if options.get("readOnly"):
            self.setReadOnly(True)
        self.valueChanged.connect(self.input_field_changed)

    def set_value(self, value: int) -> None:
        """Setter for widget value"""
        self.setValue(int(value))

    def get_value(self) -> int:
        """Getter for widget value"""
        val: int = self.value()
        return int(val) if val else None

    def close(self):
        """Close widget and disconnect signals"""
        self.valueChanged.disconnect(self.input_field_changed)


class DoubleSpinBox(qt_import.QDoubleSpinBox, ValueWidget):
    """Standard float (spinbox) widget"""

    # CHANGED_COLOR = qt_import.QColor(255, 165, 0)

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QDoubleSpinBox.__init__(self, parent)
        ValueWidget.__init__(self, gui_root_widget, options)
        self.lineEdit().setAlignment(qt_import.Qt.AlignLeft)
        if "unit" in options:
            self.setSuffix(" " + options["unit"])
        if "default" in options:
            val = float(options["default"])
            self.setValue(val)
        if "maximum" in options:
            self.setMaximum(float(options["maximum"]))
        if "minimum" in options:
            self.setMinimum(float(options["minimum"]))
        if "tooltip" in options:
            self.setToolTip(options["tooltip"])
        if options.get("readOnly"):
            self.setReadOnly(True)
        self.valueChanged.connect(self.input_field_changed)

    def set_value(self, value: float) -> None:
        """Setter for widget value"""
        self.setValue(float(value))

    def get_value(self) -> float:
        """Getter for widget value"""
        val: float = self.value()
        return float(val) if val else None

    def close(self):
        """Close widget and disconnect signals"""
        self.valueChanged.disconnect(self.input_field_changed)


class CheckBox(qt_import.QCheckBox, ValueWidget):
    """Standard Boolean (CheckBox) widget"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QCheckBox.__init__(self, options.get("uiLabel"), parent)
        ValueWidget.__init__(self, gui_root_widget, options)
        self.setCheckState(
            qt_import.Qt.Checked if options.get("default") else qt_import.Qt.Unchecked
        )
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.stateChanged.connect(self.input_field_changed)

    def set_value(self, value: bool) -> None:
        """Setter for widget value"""
        self.setChecked(value)

    def get_value(self) -> bool:
        """Getter for widget value"""
        return self.isChecked()

    def close(self):
        """Close widget and disconnect signals"""
        self.stateChanged.disconnect(self.input_field_changed)


class LocalQGroupBox(qt_import.QGroupBox):
    """Wrapper around QGroupBox to provide is_hidden attribute"""

    is_hidden: bool = False


def create_widgets(
    schema: Dict[str, Any],
    ui_schema: Dict[str, Any],
    field_name: Optional[str] = None,
    parent_widget: Optional[qt_import.QWidget] = None,
    gui_root_widget: Optional[LayoutWidget] = None,
    is_hidden: bool = False,
) -> qt_import.QWidget:
    """Recursive widget creation function

    Args:
        schema :  jsonschema
        ui_schema : ui:schema dictionary for widget being created
        field_name (: Unique name of field (or container) being created.
                          Equal to tag in ui_schema, and used as variable_name
        parent_widget: parent widget
        gui_root_widget : root (layoutWidget) widget
        is_hidden : is widget hidden?

    Returns (qt_import.QWidget):

    NB the input data structures differ from standard ui:schema usage
    fields and layout are taken from the ui:schema, so the schema order is mandatory
    there are grouping constructs corresponding to columns and boxes in the ui:schema
    that do not match any object in the jsonschema.
    """

    is_top_object: bool = gui_root_widget is None

    default_container_name: str = "vertical_box"

    fields: Dict[str, Any] = schema["properties"]

    field_data: Optional[Dict[str, Any]] = fields.get(field_name)
    widget_name: Optional[str] = ui_schema.get("ui:widget")
    if field_data:
        # This is an actual data field
        options: Dict[str, Any] = field_data.copy()
        options["variable_name"] = field_name

        if not widget_name:
            if "enum" in options:
                widget_name = "select"
            else:
                widget_name = field_data.get("type")

        options.update(ui_schema.get("ui:options", {}))
        if ui_schema.get("ui:readOnly"):
            options["readOnly"] = True
        if is_hidden:
            options["hidden"] = True
        if widget_name == "textdisplay":
            widget = TextDisplay(parent_widget, options)
        else:
            widget: qt_import.QWidget = WIDGET_CLASSES[widget_name](
                parent_widget, gui_root_widget, options
            )
            gui_root_widget.parameter_widgets[field_name] = widget
    else:
        # This is a container field
        title = ui_schema.get("ui:title")
        widget_name = widget_name or default_container_name
        spacing = 6
        if is_top_object:
            # Top of schema
            options = ui_schema["ui:options"]
            widget: qt_import.QWidget = LayoutWidget(options)
            gui_root_widget = widget
            spacing = 20
        elif title:
            widget: qt_import.QWidget = LocalQGroupBox(title, parent=parent_widget)
        else:
            widget: qt_import.QWidget = LocalQGroupBox(parent=parent_widget)
        layout_class = WIDGET_CLASSES[widget_name]
        layout: qt_import.QWidget = layout_class(widget)
        layout.setSpacing(spacing)
        widget.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        layout.populate_widget(schema, ui_schema, gui_root_widget)
    if is_top_object:
        # This is the root widget
        # Now everything is populated, put the hidden widgets in as data holders
        for fname, field in fields.items():
            if fname not in gui_root_widget.parameter_widgets:
                if field.get("type") != "textdisplay":
                    # Any field not being displayed is by definition hidden
                    # NB should not happen much,
                    # but might be used to temporarily hide fields
                    create_widgets(
                        schema,
                        field,
                        fname,
                        parent_widget=gui_root_widget,
                        gui_root_widget=gui_root_widget,
                        is_hidden=True,
                    )
    #
    return widget


class ColumnGridWidget(qt_import.QGridLayout):
    """Gridded layout, content specified by column"""

    col_spacing = " " * 7

    def __init__(self, parent):
        """
        Args:
            parent (qtimport.QtWidget:
        """
        super().__init__(parent)
        self.is_hidden: bool = False

    def populate_widget(
        self,
        schema: Dict[str, Any],
        ui_schema: Dict[str, Any],
        gui_root_widget: LayoutWidget,
    ):
        """Create contents and add them to container widger"""
        fields: Dict[str, Any] = schema["properties"]
        maxrownum: int = 0
        rownum: int = 0
        colnames: list = ui_schema["ui:order"] or list(
            x for x in ui_schema if not x.startswith("ui:")
        )
        maxcolnum: int = 2 * len(colnames) - 1
        for colnum, colname in enumerate(colnames):
            column: Dict[str, Any] = ui_schema[colname]
            col1: int = 2 * colnum
            for rownum, rowname in enumerate(
                (column["ui:order"])
                or list(x for x in column if not x.startswith("ui:"))
            ):
                field: Dict[str, Any] = fields.get(rowname)
                ui_field: Dict[str, Any] = column.get(rowname) or field
                new_widget: qt_import.QWidget = create_widgets(
                    schema,
                    ui_field,
                    rowname,
                    self.parent(),
                    gui_root_widget,
                )
                if field:
                    widget_type: str = ui_field.get("ui:widget") or field.get(
                        "type", "string"
                    )
                    if widget_type in ("textarea", "selection_table"):
                        self.setRowStretch(rownum, 8)
                        self.setColumnStretch(colnum, 8)
                    title: Optional[str] = field.get("title") or ui_field.get(
                        "ui:title"
                    )
                    if title:
                        if widget_type in (
                            "textarea",
                            "selection_table",
                            "textdisplay",
                        ):
                            # Special case - title goes above
                            outer_box: LocalQGroupBox = LocalQGroupBox(
                                title,
                                parent=self.parent(),
                            )
                            self.addWidget(
                                outer_box,
                                rownum,
                                col1,
                                1,
                                2,
                            )
                            outer_layout: qt_import.QVBoxLayout = (
                                qt_import.QVBoxLayout()
                            )
                            outer_box.setLayout(outer_layout)
                            outer_layout.addWidget(new_widget)
                            outer_layout.setStretch(8, 8)
                        elif not new_widget.is_hidden:
                            new_widget.setSizePolicy(
                                qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Fixed
                            )
                            if col1:
                                # Add spacing to columns after the first
                                title = self.col_spacing + title
                            label: qt_import.QLabel = qt_import.QLabel(
                                title, self.parent()
                            )
                            self.addWidget(
                                label,
                                rownum,
                                col1,
                                qt_import.Qt.AlignRight | qt_import.Qt.AlignTop,
                            )
                            self.addWidget(
                                new_widget,
                                rownum,
                                col1 + 1,
                                qt_import.Qt.AlignLeft | qt_import.Qt.AlignTop,
                            )
                    else:
                        self.addWidget(
                            new_widget,
                            rownum,
                            col1,
                            1,
                            2,
                        )
                else:
                    title: Optional[str] = ui_schema.get("ui:title")
                    if title:
                        outer_box: LocalQGroupBox = LocalQGroupBox(
                            title, parent=self.parent()
                        )
                        self.addWidget(
                            outer_box,
                            rownum,
                            col1,
                            1,
                            2,
                        )
                        outer_layout: qt_import.QVBoxLayout = qt_import.QVBoxLayout()
                        outer_box.setLayout(outer_layout)
                        outer_layout.addWidget(
                            new_widget,
                            0,
                        )
                    else:
                        self.addWidget(
                            new_widget,
                            rownum,
                            col1,
                            1,
                            2,
                        )
            maxrownum = max(maxrownum, rownum)
        # Add spacer to compress layout
        spacer_item: qt_import.QSpacerItem = qt_import.QSpacerItem(
            6,
            6,
            qt_import.QSizePolicy.Expanding,
            qt_import.QSizePolicy.Expanding,
        )
        self.addItem(spacer_item, maxrownum + 1, maxcolnum + 1)


class VerticalBox(ColumnGridWidget):
    """Container, treated as a single column gridded box,
    with input not grouped in columns"""

    def populate_widget(
        self,
        schema: Dict[str, Any],
        ui_schema: Dict[str, Any],
        gui_root_widget: LayoutWidget,
    ):
        """Create contents and add them to container widger"""
        wrap_schema: Dict[str, Any] = {}
        col_schema: Dict[str, Any] = {}
        wrap_schema["column"] = col_schema
        self.is_hidden: bool = False
        for tag, val in ui_schema.items():
            if tag.startswith("ui:"):
                wrap_schema[tag] = val
            else:
                col_schema[tag] = val
        col_schema["ui:order"] = wrap_schema["ui:order"]
        wrap_schema["ui:order"] = ("column",)
        #
        super().populate_widget(schema, wrap_schema, gui_root_widget)


class HorizontalBox(ColumnGridWidget):
    """Container, treated as a single row gridded box,
    with input not grouped in columns"""

    def populate_widget(
        self,
        schema: Dict[str, Any],
        ui_schema: Dict[str, Any],
        gui_root_widget: LayoutWidget,
    ):
        """Create contents and add them to container widger"""
        wrap_schema: Dict[str, Any] = {}
        self.is_hidden: bool = False
        title: Optional[str] = ui_schema.get("ui:title")
        if title:
            wrap_schema["ui:title"] = title
        new_order: list = []
        wrap_schema["ui:order"] = new_order
        for tag in ui_schema["ui:order"]:
            colname: str = tag + "_col"
            new_order.append((colname))
            dd0: Dict[str, Any] = {"ui:order": [tag]}
            if tag in ui_schema:
                dd0[tag] = ui_schema[tag]
            wrap_schema[colname] = dd0
        #
        super().populate_widget(schema, wrap_schema, gui_root_widget)


class SelectionTable(qt_import.QTableWidget, ValueWidget):
    """Read-only table for data display and selection"""

    def __init__(
        self,
        parent: qt_import.QWidget,
        gui_root_widget: LayoutWidget,
        options: Dict[str, Any],
    ):
        qt_import.QTableWidget.__init__(self, parent)
        ValueWidget.__init__(self, gui_root_widget, options)
        header: str = options["header"]

        self.setFrameShape(qt_import.QFrame.StyledPanel)
        self.setFrameShadow(qt_import.QFrame.Sunken)
        self.setContentsMargins(0, 3, 0, 3)
        self.setColumnCount(len(header))
        self.setSelectionMode(qt_import.QTableWidget.SingleSelection)
        self.setHorizontalHeaderLabels(header)
        self.horizontalHeader().setDefaultAlignment(qt_import.Qt.AlignLeft)
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Expanding
        )
        self.setSizeAdjustPolicy(qt_import.QAbstractScrollArea.AdjustToContents)
        self.setFont(qt_import.QFont("Courier"))

        hdr: qt_import.QHeaderView = self.horizontalHeader()
        hdr.setSectionResizeMode(0, qt_import.QHeaderView.Stretch)
        for idx in range(1, len(header)):
            hdr.setSectionResizeMode(idx, qt_import.QHeaderView.ResizeToContents)

        highlights: Dict[int, Dict[int, str]] = options.get("highlights")
        for idx, data in enumerate(options["content"]):
            self.populate_column(idx, data, highlights)

        cell_indx = options.get("select_cell", (0, 0))
        self.setCurrentCell(*cell_indx)
        self.currentCellChanged.connect(self.input_field_changed)

    def resizeData(self, iii: int):
        """Dummy method, recommended by Qt docs when not using std cell widgets"""
        pass

    def populate_column(
        self,
        colnum: int,
        values: Sequence,
        highlights: Dict[int, Dict[int, str]] = None,
    ):
        """Fill values into column, extending if necessary"""
        if len(values) > self.rowCount():
            self.setRowCount(len(values))
        for rownum, text in enumerate(values):
            wdg = qt_import.QLineEdit(self)
            wdg.setFont(qt_import.QFont("Courier"))
            wdg.setReadOnly(True)
            wdg.setText(str(text))
            wdg.setContentsMargins(1, 1, 1, 1)
            dd0 = highlights.get(rownum)
            if dd0:
                colourname = dd0.get(colnum)
            else:
                colourname = None
            if colourname is not None:
                colors.set_widget_color(
                    wdg, ColourMap[colourname], qt_import.QPalette.Base
                )
            self.setCellWidget(rownum, colnum, wdg)

    def get_value(self):
        """Get value - list of cell contents for selected cell"""
        row_id = self.currentRow()
        col_id = self.currentColumn()
        if not self.cellWidget(row_id, col_id):
            logging.getLogger("user_log").warning(
                "Select a cell of the table, and then press [Continue]"
            )
        return self.cellWidget(row_id, col_id).text()

    def set_value(self, value):
        """Set current cell that matches list of cell contents

        This is not really useful (you would use the setCurrentCell method instead)
        But the method is there for consistency with the ValueWIdget superclass"""
        ncols: int = self.columnCount()
        for row_id in range(self.rowCount()):
            for col_id in range(self.columnCount()):
                if value == self.cellWidget(row_id, col_id).text():
                    self.setCurrentCell(row_id, col_id)
                    return
        raise ValueError("Value %s not found in widget %s" % (value, self.get_name()))

    def colour_widget(self, highlight: str) -> None:
        """Dummy function, to disable background colouring of SelectionTable"""
        return

    def close(self):
        """Close widget and disconnect signals"""
        self.currentCellChanged.disconnect(self.input_field_changed)


# Class is selected from ui:widget or, failing that, from type
WIDGET_CLASSES = {
    "label": qt_import.QLabel,
    "number": FloatString,
    "string": LineEdit,
    "boolean": CheckBox,
    "integer": FloatString,
    "textarea": TextEdit,
    "spinbox": IntSpinBox,
    "float": DoubleSpinBox,
    "select": Combo,
    "column_grid": ColumnGridWidget,
    "horizontal_box": HorizontalBox,
    "vertical_box": VerticalBox,
    "selection_table": SelectionTable,
}
