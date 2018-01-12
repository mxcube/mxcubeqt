import qt
import qttable
from paramsgui import FieldsWidget

class SelectionTable(qttable.QTable):
    """Read-only table for data display and selection"""
    def __init__(self, parent=None, name="selection_table", header=None):
        qttable.QTable.__init__(self, parent, name)
        if not header:
            raise ValueError("DisplayTable must be initialised with header")

        self.setNumCols(len(header))
        self.setSelectionMode(qttable.QTable.SingleRow)
        self.horizontalHeader().setFont(qt.QFont("Courier"))
        self.horizontalHeader().setStretchEnabled(True, -1)
        for ii, text in enumerate(header):
            self.horizontalHeader().setLabel(ii, text)
            self.setColumnReadOnly(ii, True)
            # self.setColumnStretchable(ii, True)
        # self.setSizePolicy(qt.QSizePolicy.Expanding,
        #                                  qt.QSizePolicy.Expanding)
        self.horizontalHeader().adjustHeaderSize()

    def resizeData(self, ii):
        """Dummy method, recommended by docs when not using std cell widgets"""
        pass

    def populateColumn(self, colNum, values, colours=None):
        """Fill values into column, extending if necessary"""
        if len(values) > self.numRows():
            self.setNumRows(len(values))
        for rowNum, text in enumerate(values):
            wdg = qt.QLineEdit(self)
            wdg.setFont(qt.QFont("Courier"))
            wdg.setReadOnly(True)
            wdg.setText(text)
            if colours:
                colour = colours[rowNum]
                if colour:
                    wdg.setPaletteBackgroundColor(getattr(qt.Qt, colour))
            self.setCellWidget(rowNum, colNum, wdg)

    def get_value(self):
        """Get value - list of cell contents for selected row"""
        row_id = self.selection(0).anchorRow()
        return [self.cellWidget(row_id, ii).text()
                for ii in range(self.numCols())]

class GphlDataDialog(qt.QDialog):

    def __init__(self, parent = None, name = None, fl = 0):
        qt.QWidget.__init__(self, parent, name, fl)

        # AsyncResult to return values
        self._async_result = None
        
        # Layout
        qt.QVBoxLayout(self)
        main_layout = self.layout()
        main_layout.setSpacing(10)
        main_layout.setMargin(6)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        self.setCaption('GPhL Workflow parameters')

        # Info box
        self.info_gbox = qt.QVGroupBox('Info', self, "info_gbox")
        main_layout.addWidget(self.info_gbox)
        self.info_text = qt.QTextEdit(self.info_gbox, 'info_text')
        self.info_text.setTextFormat(0) # PlainText
        self.info_text.setFont(qt.QFont("Courier"))
        self.info_text.setReadOnly(True)

        # Special parameter box
        self.cplx_gbox = qt.QVGroupBox('Indexing solution', self,
                                         "cplx_gbox")
        main_layout.addWidget(self.cplx_gbox)
        self.cplx_widget = None

        # Parameter box
        self.parameter_gbox = qt.QVGroupBox('Parameters', self,
                                           "parameter_gbox")
        main_layout.addWidget(self.parameter_gbox)
        self.params_widget = None

        # Button bar
        button_layout = qt.QHBoxLayout(None,0,6,"button_layout")
        hspacer = qt.QSpacerItem(1,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        button_layout.addItem(hspacer)
        self.continue_button = qt.QPushButton('Continue', self,
                                              'continue_button')
        button_layout.addWidget(self.continue_button)
        self.cancel_button = qt.QPushButton('Abort', self, "cancel_button")
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        qt.QObject.connect(self.continue_button, qt.SIGNAL("clicked()"),
                           self.continue_button_click)

        qt.QObject.connect(self.cancel_button, qt.SIGNAL("clicked()"),
                           self.cancel_button_click)

        self.resize(qt.QSize(1018,472).expandedTo(self.minimumSizeHint()))
        self.clearWState(qt.Qt.WState_Polished)

    def continue_button_click(self):
        result = {}
        if self.parameter_gbox.isVisible():
            result.update(self.params_widget.get_parameters_map())
        if self.cplx_gbox.isVisible():
            result['_cplx'] = self.cplx_widget.get_value()
        self.accept()
        self._async_result.set(result)
        self._async_result = None

    def cancel_button_click(self):
        self.reject()
        self.parent.workflow_model.workflow_hwobj.abort("Manual abort")

    def open_dialog(self, field_list, async_result):

        self._async_result = async_result

        # get special parameters
        parameters = []
        info = None
        cplx = None
        for dd in field_list:
            if info is None and dd.get('variableName') == '_info':
                # Info text - goes to info_gbox
                info = dd
            elif cplx is None and dd.get('variableName') == '_cplx':
                # Complex parameter - goes to cplx_gbox
                cplx = dd
            else:
                parameters.append(dd)

        # Info box
        if info is None:
            self.info_text.setText('')
            self.info_gbox.setTitle('Info')
            self.info_gbox.hide()
        else:
            self.info_text.setText(info.get('defaultValue'))
            self.info_gbox.setTitle(info.get('uiLabel'))
            self.info_gbox.show()

        # Complex box
        if self.cplx_widget:
            self.cplx_widget.close()
        if cplx is None:
            self.cplx_gbox.hide()
        else:
            if cplx.get('type') == 'selection_table':
                self.cplx_widget = SelectionTable(self.cplx_gbox, 'cplx_widget',
                                                cplx['header'])
                self.cplx_gbox.setTitle(cplx.get('uiLabel'))
                for ii,values in enumerate(cplx['defaultValue']):
                    self.cplx_widget.populateColumn(ii, values,
                                                    colours=cplx.get('colours'))
                self.cplx_gbox.show()

            else:
                raise NotImplementedError(
                    "GPhL complex widget type %s not recognised for parameter _cplx"
                    % repr(cplx.get('type'))
                )

        # parameters widget
        if self.params_widget is not None:
            self.params_widget.close()
            self.params_widget = None
        if parameters:
            self.params_widget = FieldsWidget(fields=parameters,
                                              parent=self.parameter_gbox)

            values ={}
            for dd in field_list:
                name = dd['variableName']
                value = dd.get('defaultValue')
                if value is not None:
                    dd[name] = value
            self.params_widget.set_values(values)
            self.parameter_gbox.show()
        else:
            self.parameter_gbox.hide()

        self.show()
        self.setEnabled(True)
