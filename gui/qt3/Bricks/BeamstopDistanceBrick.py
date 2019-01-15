"""
"""
import qt
import logging
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons
from BlissFramework.Utils.CustomWidgets import DialogButtonsBar
from BlissFramework.Utils import widget_colors


class BeamstopDistanceBrick(BlissWidget):
    CONNECTED_COLOR = widget_colors.LIGHT_GREEN
    CHANGED_COLOR = qt.QColor(255, 165, 0)
    OUTLIMITS_COLOR = widget_colors.LIGHT_RED

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("mnemonic", "string", "")
        self.addProperty("icons", "string", "")
        self.addProperty("formatString", "formatString", "###.##")

        self.beamstop_hwobj = None

        self.top_gbox = qt.QHGroupBox("Beamstop distance", self)
        self.top_gbox.setInsideMargin(4)
        self.top_gbox.setInsideSpacing(2)

        self.params_widget = qt.QWidget(self.top_gbox)
        qt.QGridLayout(self.params_widget, 2, 3, 0, 2)

        label1 = qt.QLabel("Current:", self.params_widget)
        label1.setFixedWidth(70)
        self.params_widget.layout().addWidget(label1, 0, 0)

        self.current_position_ledit = qt.QLineEdit(self.params_widget)
        self.current_position_ledit.setReadOnly(True)
        self.params_widget.layout().addWidget(self.current_position_ledit, 0, 1)

        label2 = qt.QLabel("Set to:", self.params_widget)
        label2.setFixedWidth(70)
        self.params_widget.layout().addWidget(label2, 1, 0)

        self.new_position_ledit = qt.QLineEdit(self.params_widget)
        self.new_position_ledit.setAlignment(qt.QWidget.AlignRight)
        self.params_widget.layout().addWidget(self.new_position_ledit, 1, 1)
        self.new_position_ledit.setValidator(qt.QDoubleValidator(self))
        self.new_position_ledit.setPaletteBackgroundColor(
            BeamstopDistanceBrick.CONNECTED_COLOR
        )

        qt.QObject.connect(
            self.new_position_ledit, qt.SIGNAL("returnPressed()"), self.change_position
        )
        qt.QObject.connect(
            self.new_position_ledit,
            qt.SIGNAL("textChanged(const QString &)"),
            self.input_field_changed,
        )

        self.instanceSynchronize("new_position_ledit")

        qt.QVBoxLayout(self)
        self.layout().addWidget(self.top_gbox)

    def propertyChanged(self, property, oldValue, newValue):
        if property == "mnemonic":
            if self.beamstop_hwobj is not None:
                self.disconnect(
                    self.beamstop_hwobj, qt.PYSIGNAL("deviceReady"), self.connected
                )
                self.disconnect(
                    self.beamstop_hwobj,
                    qt.PYSIGNAL("deviceNotReady"),
                    self.disconnected,
                )
                self.disconnect(
                    self.beamstop_hwobj,
                    qt.PYSIGNAL("beamstopDistanceChanged"),
                    self.beamstop_distance_changed,
                )
            self.beamstop_hwobj = self.getHardwareObject(newValue)
            if self.beamstop_hwobj is not None:
                self.connect(
                    self.beamstop_hwobj, qt.PYSIGNAL("deviceReady"), self.connected
                )
                self.connect(
                    self.beamstop_hwobj,
                    qt.PYSIGNAL("deviceNotReady"),
                    self.disconnected,
                )
                self.connect(
                    self.beamstop_hwobj,
                    qt.PYSIGNAL("beamstopDistanceChanged"),
                    self.beamstop_distance_changed,
                )
                if self.beamstop_hwobj.isReady():
                    self.connected()
                    self.beamstop_hwobj.update_values()
                else:
                    self.disconnected()
            else:
                self.disconnected()
        else:
            BlissWidget.propertyChanged(self, property, oldValue, newValue)

    def input_field_changed(self, text):
        text = str(text)
        if text == "":
            self.new_position_ledit.setPaletteBackgroundColor(
                BeamstopDistanceBrick.CONNECTED_COLOR
            )
        else:
            try:
                val = float(text)
            except (TypeError, ValueError):
                widget_color = BeamstopDistanceBrick.OUTLIMITS_COLOR
            else:
                widget_color = BeamstopDistanceBrick.CHANGED_COLOR
                if self.beamstop_limits is not None:
                    if val < self.beamstop_limits[0] or val > self.beamstop_limits[1]:
                        widget_color = BeamstopDistanceBrick.OUTLIMITS_COLOR

            self.new_position_ledit.setPaletteBackgroundColor(widget_color)

    def change_position(self):
        try:
            val = float(str(self.new_position_ledit.text()))
        except (ValueError, TypeError):
            return

        if self.beamstop_limits is not None:
            if val < self.beamstop_limits[0] or val > self.beamstop_limits[1]:
                return

        self.beamstop_hwobj.set_positions(val)
        self.new_position_ledit.setText("")

    def connected(self):
        self.beamstop_limits = (0, 200)
        self.top_gbox.setEnabled(True)

    def disconnected(self):
        self.beamstop_limits = None
        self.top_gbox.setEnabled(False)

    def beamstop_distance_changed(self, value):
        if value is None:
            return
        if value < 0:
            self.current_position_ledit.setText("")
        else:
            value_str = self["formatString"] % value
            self.current_position_ledit.setText("%s mm" % value_str)
