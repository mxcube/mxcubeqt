from qt import *


from widgets.routine_dc_char_widget_layout import RoutineDCWidgetLayout
from widgets.sad_char_widget_layout import SADWidgetLayout
from widgets.radiation_damage_char_widget_layout import RadiationDamageWidgetLayout


class CharTypeWidget(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("CharTypeWidget")

        #
        # Layout
        #
        vlayout = QVBoxLayout(self, 0, 6, "hlayout")

        self.charact_type_gbox = QHGroupBox(self, "group_box")
        self.charact_type_gbox.setTitle("Characterisation type")
        self.charact_type_gbox.layout().setSpacing(9)
        self.charact_type_gbox.layout().setMargin(11)

        # Fix the widths of the widgets to make the layout look nicer,
        # and beacuse the qt layout engine is so tremendosly good.
        self.charact_type_gbox.setFixedWidth(621)
        self.charact_type_gbox.setFixedHeight(220)

        self.charact_type_tbox = QToolBox(self.charact_type_gbox, "tool_box")
        self.routine_dc_page = RoutineDCWidgetLayout(
            self.charact_type_tbox, "routine_dc_widget"
        )
        self.routine_dc_page.setBackgroundMode(QWidget.PaletteBackground)
        self.sad_page = SADWidgetLayout(self.charact_type_tbox, "sad_widget")
        self.sad_page.setBackgroundMode(QWidget.PaletteBackground)
        self.rad_damage_page = RadiationDamageWidgetLayout(
            self.charact_type_tbox, "radiation_damage_widget"
        )
        self.rad_damage_page.setBackgroundMode(QWidget.PaletteBackground)

        self.charact_type_tbox.addItem(self.routine_dc_page, "Routine-DC")
        self.charact_type_tbox.addItem(self.sad_page, "SAD")
        self.charact_type_tbox.addItem(self.rad_damage_page, "Radiation damage")

        vlayout.addWidget(self.charact_type_gbox)
        vlayout.addStretch(10)

        #
        # Logic
        #
        QObject.connect(
            self.routine_dc_page.dose_limit_cbx,
            SIGNAL("toggled(bool)"),
            self.enable_dose_ledit,
        )

        QObject.connect(
            self.routine_dc_page.time_limit_cbx,
            SIGNAL("toggled(bool)"),
            self.enable_time_ledit,
        )

        QObject.connect(
            self.routine_dc_page.dose_time_bgroup,
            SIGNAL("clicked(int)"),
            self._toggle_time_dose,
        )

        self._toggle_time_dose(self.routine_dc_page.dose_time_bgroup.selectedId())

    def enable_time_ledit(self, state):
        self.routine_dc_page.time_ledit.setEnabled(state)

    def enable_dose_ledit(self, state):
        self.routine_dc_page.dose_ledit.setEnabled(state)

    def _toggle_time_dose(self, index):
        if index is 1:
            self.routine_dc_page.dose_ledit.setEnabled(False)
            self.routine_dc_page.dose_limit_cbx.setEnabled(False)
            self.routine_dc_page.time_limit_cbx.setEnabled(True)
            self.routine_dc_page.radiation_damage_cbx.setEnabled(True)
            self.enable_time_ledit(self.routine_dc_page.time_limit_cbx.isOn())
        elif index is 0:
            self.routine_dc_page.dose_limit_cbx.setEnabled(True)
            self.enable_dose_ledit(self.routine_dc_page.dose_limit_cbx.isOn())
            self.routine_dc_page.time_ledit.setEnabled(False)
            self.routine_dc_page.time_limit_cbx.setEnabled(False)
            self.routine_dc_page.radiation_damage_cbx.setEnabled(False)
            self.routine_dc_page.radiation_damage_cbx.setOn(True)
        elif index is -1:
            self.routine_dc_page.dose_ledit.setEnabled(False)
            self.routine_dc_page.time_ledit.setEnabled(False)
            self.routine_dc_page.time_limit_cbx.setEnabled(False)
            self.routine_dc_page.dose_limit_cbx.setEnabled(False)
            self.routine_dc_page.radiation_damage_cbx.setEnabled(False)

    def toggle_time_dose(self):
        index = self.routine_dc_page.dose_time_bgroup.selectedId()
        self._toggle_time_dose(index)
