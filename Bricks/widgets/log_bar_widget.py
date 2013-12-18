import time
import qt
import gevent

from BlissFramework.Utils import widget_colors

class LogBarWidget(qt.QWidget):
    def __init__(self, parent = None, name = "log_bar_widget", fl = 0):
        qt.QWidget.__init__(self, parent, name, fl)

        self.text_edit = qt.QTextEdit(self, "text_edit")
        self.text_edit.setMinimumSize(qt.QSize(0, 55))
        self.text_edit.setMaximumSize(qt.QSize(32767, 55))
        self.text_edit.setTextFormat(qt.QTextEdit.RichText)
        main_layout = qt.QHBoxLayout(self)
        main_layout.addWidget(self.text_edit)

    def toggle_background_color(self):
        gevent.spawn(self._toggle_background_color)

    def _toggle_background_color(self):
        for i in range(0, 3):
            self.set_background_color(widget_colors.LIGHT_RED)
            time.sleep(0.1)
            self.set_background_color(widget_colors.WHITE)
            time.sleep(0.1)

    def set_background_color(self, qt_color):
        brush = self.text_edit.paper()
        brush.setColor(qt_color)
        self.text_edit.setPaper(brush)
            
