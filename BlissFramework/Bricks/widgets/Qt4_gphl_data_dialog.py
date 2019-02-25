"""GPhL runtime-set parameter input widget. """

import QtImport
from Qt4_paramsgui import FieldsWidget
from Utils import Qt4_widget_colors

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class ParameterDialogWidget(QtImport.QWidget):

    def __init__(self, parent=None, name='gphl_parameter_dialog_widget'):
        QtImport.QWidget.__init__(self,parent)
        if name is not None:
            self.setObjectName(name)

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------

         # Internal variables -------------------------------------------------

        # Graphic elements ----------------------------------------------------

    def get_parameters_map(self):
        """Get key:value dictionary of parameter values"""
        pass

    def set_values(self, values_dict):
        """set parameter values from input dictionary"""


class SelectionTable(QtImport.QTableWidget):
    """Read-only table for data display and selection"""
    def __init__(self, parent=None, name="selection_table", header=None):
        QtImport.QTableWidget.__init__(self, parent)
        if not header:
            raise ValueError("DisplayTable must be initialised with header")

        self.setObjectName(name)
        self.setFrameShape(QtImport.QFrame.StyledPanel)
        self.setFrameShadow(QtImport.QFrame.Sunken)
        self.setContentsMargins(0, 3, 0, 3)
        self.setColumnCount(len(header))
        self.setSelectionMode(QtImport.QTableWidget.SingleSelection)
        self.setHorizontalHeaderLabels(header)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding,
                           QtImport.QSizePolicy.Expanding)
        self.setFont(QtImport.QFont("Courier"))

        hdr = self.horizontalHeader()
        hdr.setResizeMode(0, QtImport.QHeaderView.Stretch)
        for ii in range(1, len(header)):
            hdr.setResizeMode(ii, QtImport.QHeaderView.ResizeToContents)

    def resizeData(self, ii):
        """Dummy method, recommended by docs when not using std cell widgets"""
        pass

    def populateColumn(self, colNum, values, colours=None):
        """Fill values into column, extending if necessary"""
        if len(values) > self.rowCount():
            self.setRowCount(len(values))
        for rowNum, text in enumerate(values):
            wdg = QtImport.QLineEdit(self)
            wdg.setFont(QtImport.QFont("Courier"))
            wdg.setReadOnly(True)
            wdg.setText(str(text))
            if colours:
                colour = colours[rowNum]
                if colour:
                    Qt4_widget_colors.set_widget_color(
                        wdg,
                        getattr(Qt4_widget_colors, colour),
                        QtImport.QPalette.Base
                    )
                    # wdg.setBackground(getattr(QtImport.QColor, colour))
            self.setCellWidget(rowNum, colNum, wdg)

    def get_value(self):
        """Get value - list of cell contents for selected row"""
        row_id = self.currentRow()
        return [self.cellWidget(row_id, ii).text()
                for ii in range(self.columnCount())]

class GphlDataDialog(QtImport.QDialog):

    continueClickedSignal = QtImport.pyqtSignal()

    def __init__(self, parent=None, name=None, fl=0):
        QtImport.QDialog.__init__(self, parent, QtImport.Qt.WindowFlags(fl))

        if name is not None:
            self.setObjectName(name)


        # Internal variables --------------------------------------------------
        # AsyncResult to return values
        self._async_result = None
        
        # Layout
        QtImport.QVBoxLayout(self)
        main_layout = self.layout()
        main_layout.setSpacing(10)
        main_layout.setMargin(6)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding,
                           QtImport.QSizePolicy.Expanding)

        self.setWindowTitle('GPhL Workflow parameters')

        # Info box
        self.info_gbox = QtImport.QGroupBox('Info', self)
        QtImport.QVBoxLayout(self.info_gbox)
        main_layout.addWidget(self.info_gbox)
        self.info_text = QtImport.QTextEdit(self.info_gbox)
        self.info_text.setFont(QtImport.QFont("Courier"))
        self.info_text.setReadOnly(True)
        self.info_gbox.layout().addWidget(self.info_text)

        # Special parameter box
        self.cplx_gbox = QtImport.QGroupBox('Indexing solution', self)
        QtImport.QVBoxLayout(self.cplx_gbox)
        main_layout.addWidget(self.cplx_gbox)
        self.cplx_gbox.setSizePolicy(QtImport.QSizePolicy.Expanding,
                                          QtImport.QSizePolicy.Expanding)
        self.cplx_widget = None

        # Parameter box
        self.parameter_gbox = QtImport.QGroupBox('Parameters', self,)
        main_layout.addWidget(self.parameter_gbox)
        self.parameter_gbox.setSizePolicy(QtImport.QSizePolicy.Expanding,
                                          QtImport.QSizePolicy.Expanding)
        self.params_widget = None

        # Button bar
        button_layout = QtImport.QHBoxLayout(None)
        hspacer = QtImport.QSpacerItem(1, 20, QtImport.QSizePolicy.Expanding,
                                    QtImport.QSizePolicy.Minimum)
        button_layout.addItem(hspacer)
        self.continue_button = QtImport.QPushButton('Continue', self)
        button_layout.addWidget(self.continue_button)
        self.cancel_button = QtImport.QPushButton('Abort', self)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.continue_button.clicked.connect(self.continue_button_click)
        self.cancel_button.clicked.connect(self.cancel_button_click)

        self.resize(QtImport.QSize(1018,472).expandedTo(self.minimumSizeHint()))
        # self.clearWState(QtImport.WState_Polished)

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
        self.parent()._workflow_hwobj.abort("Manual abort")

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
                self.cplx_gbox.layout().addWidget(self.cplx_widget)
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
