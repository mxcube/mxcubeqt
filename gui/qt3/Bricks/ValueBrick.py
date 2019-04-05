import qt
import traceback

from BlissFramework import BaseComponents

__category__ = "mxCuBE_v3"


class ValueBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty("hwobj", "string", "")
        self.addProperty("titel", "string", "")
        self.addProperty("unit", "string", "")

        self.value_label = qt.QLabel(self)
        self.prefix_label = qt.QLabel(self)
        self.postfix_label = qt.QLabel(self)
        self.spacer = qt.QSpacerItem(
            1, 20, qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )

        qt.QHBoxLayout(self)

        self.layout().addWidget(self.prefix_label)
        self.layout().addItem(self.spacer)
        self.layout().addWidget(self.value_label)
        self.layout().addWidget(self.postfix_label)

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Overriding BaseComponents.BlissWidget (propertyChanged object)
        run method.
        """
        if property_name == "hwobj":
            hw_obj = self.getHardwareObject(new_value)

            try:
                self.value_update(hw_obj.getValue())
                hw_obj.connect("valueChange", self.value_update)
            except BaseException:
                self.value_label.setText("--.--")
                # traceback.print_exc()

        if property_name == "titel":
            self.prefix_label.setText(new_value)

        if property_name == "unit":
            self.postfix_label.setText(new_value)

    def value_update(self, value):
        self.value_label.setText("%.2f" % value)
