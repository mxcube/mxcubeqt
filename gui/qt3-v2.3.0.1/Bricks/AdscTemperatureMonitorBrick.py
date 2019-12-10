from BlissFramework import BaseComponents
import qt
import math
import logging


class TemperaturePanel(qt.QWidget):
    def __init__(self, *args):
        qt.QWidget.__init__(self, *args)

        self.nccds = 9
        self.temp_list = 9 * [None]

        self.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding
        )
        self.setMinimumWidth(90)
        self.setMinimumHeight(90)

    def setNbCcds(self, n):
        self.nccds = n
        self.update()

    def setTemperatures(self, temp_list):
        try:
            self.temp_list = map(float, temp_list[: self.nccds])
        except BaseException:
            self.temp_list = self.nccds * [None]

        self.update()

    def paintEvent(self, event):
        p = qt.QPainter()
        p.begin(self)

        n = int(math.sqrt(self.nccds))
        w = self.width()
        h = self.height()
        step_x = w / n
        step_y = h / n
        # logging.getLogger().info("%s", self.temp_list)

        for i in range(n):
            x = step_x * i
            y = step_y * i

            for j in range(n):
                t = self.temp_list[j * 3 + i]
                if t is None:
                    c_b = 255
                    c_g = 255
                    c_r = 255
                else:
                    # logging.getLogger().info("%d", j*3+i)
                    c_b = 255 - int((255 / 40.0) * t + 255)
                    if c_b > 255:
                        c_b = 255
                    elif c_b < 0:
                        c_b = 0
                    c_g = int((255 / 40.0) * t + 255)
                    if c_g > 255:
                        c_g = 0
                    elif c_g < 0:
                        c_g = 0
                    if c_g > 0 and c_b > 0:
                        c_r = 0
                    else:
                        c_r = 255 - c_b
                c = qt.QColor(c_r, c_g, c_b)
                brush = qt.QBrush(c)
                p.fillRect(
                    x + 1, j * step_y + 1, x + step_x - 1, (j + 1) * step_y - 1, brush
                )

            p.setPen(qt.QPen(qt.QColor(0, 0, 0)))
            # logging.getLogger().info("%d %d", x, y)
            p.drawLine(x, 0, x, h)
            p.drawLine(0, y, w, y)

        p.end()
        return qt.QWidget.paintEvent(self, event)


class AdscTemperatureMonitorBrick(BaseComponents.BlissWidget):
    def __init__(self, *args, **kwargs):
        BaseComponents.BlissWidget.__init__(self, *args, **kwargs)

        self.detector_ho = None

        self.addProperty("mnemonic", "string", "")
        self.addProperty("nb_ccd", "integer", 9)

        self.gbox = qt.QVGroupBox("ADSC temperature", self)
        self.gbox.setInsideSpacing(0)
        self.gbox.setAlignment(qt.QLabel.AlignCenter)
        self.lblStatus = qt.QLabel("<nobr>unknown state</nobr>", self.gbox)
        self.lblStatus.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Fixed
        )
        self.lblStatus.setPaletteBackgroundColor(qt.Qt.lightGray)
        self.lblStatus.setAlignment(qt.Qt.AlignCenter)
        self.tempPanel = TemperaturePanel(self.gbox)

        qt.QVBoxLayout(self)
        self.layout().addWidget(self.gbox)

    def temperaturesUpdated(self, t):
        status = t[0]

        if status == "COLD":
            self.lblStatus.setPaletteBackgroundColor(qt.Qt.green)
            self.lblStatus.setText("<nobr>cooling ok</nobr>")
        elif status == "WARM":
            self.lblStatus.setPaletteBackgroundColor(qt.Qt.red)
            self.lblStatus.setText("<b><nobr>detector is warm!</nobr></b>")
        else:
            return
            # self.lblStatus.setPaletteBackgroundColor(qt.Qt.gray)
            # self.lblStatus.setText("")
            # t = self["nb_ccd"]*[None]

        self.tempPanel.setTemperatures(t[1:])

    def run(self):
        if self.detector_ho is None:
            self.hide()

    def propertyChanged(self, property, old_value, new_value):
        if property == "mnemonic":
            if self.detector_ho is not None:
                self.disconnect(
                    self.detector_ho, "valueChanged", self.temperaturesUpdated
                )

            self.detector_ho = self.getHardwareObject(new_value)

            if self.detector_ho is not None:
                self.connect(self.detector_ho, "valueChanged", self.temperaturesUpdated)
        elif property == "nb_ccd":
            self.tempPanel.setNbCcds(new_value)
