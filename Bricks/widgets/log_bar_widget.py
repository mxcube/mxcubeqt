import qt


class LogBarWidget(qt.QWidget):

    def __init__(self, parent = None, name = "log_bar_widget", fl = 0):
        qt.QWidget.__init__(self, parent, name, fl)

        self.text_edit = qt.QTextEdit(self, "text_edit")
        self.text_edit.setMinimumSize(qt.QSize(0, 40))
        self.text_edit.setMaximumSize(qt.QSize(32767, 40))
        self.text_edit.setTextFormat(qt.QTextEdit.LogText)
        self.text_edit.setWordWrap(qt.QTextEdit.WidgetWidth)

        main_layout = qt.QHBoxLayout(self)
        main_layout.addWidget(self.text_edit)

        #self.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Expanding,
        #                               qt.QSizePolicy.Expanding))

        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, 
                           qt.QSizePolicy.Fixed)
