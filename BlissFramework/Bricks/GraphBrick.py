"""Graph brick"""
import time
import os
import Qwt5 as qwt
#from qwt import QwtPlot
from qt import *

from PyMca.QtBlissGraph import QtBlissGraph
from PyMca.QtBlissGraph import TimeScaleDraw
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework.Utils.CustomWidgets import QLineEditWithOkCancel
from BlissFramework import Icons

__author__ = 'Matias Guijarro'
__version__ = 1.0
__category__ = 'data_display'

class CurveSourceSelector(QDialog):    
    def __init__(self, *args):
        QDialog.__init__(self, *args)

        self.setCaption('Curve setup')

        curveNamePanel = QVBox(self)
        lblCurveName = QLabel('Curve name :', curveNamePanel)
        self.txtCurveName = QLineEdit(curveNamePanel)
        sourceSetupPanel = QVBox(self)

        QLabel('Hardware object mnemonic :', sourceSetupPanel)
        self.txtMnemonic = QLineEdit(sourceSetupPanel)
        self.cmdOK = QPushButton('OK', self)
        self.cmdClose = QPushButton('Close', self)
        curveNamePanel.setSpacing(5)
        curveNamePanel.setMargin(5)
        sourceSetupPanel.setSpacing(5)
        sourceSetupPanel.setMargin(5)

        QObject.connect(self.cmdClose, SIGNAL('clicked()'), self.reject)
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.accept)

        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(curveNamePanel, 0, Qt.AlignLeft)
        self.layout().addWidget(QLabel('<hr>', self))
        self.layout().addWidget(sourceSetupPanel)
        self.layout().addWidget(QLabel('<hr>', self))
        self.layout().addWidget(self.cmdOK)
        self.layout().addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.layout().addWidget(self.cmdClose, 0, Qt.AlignRight | Qt.AlignBottom)

    
    def setCurve(self, curve_dict, canChangeName = True):
        self.txtCurveName.setText(curve_dict['name'])
        self.txtCurveName.setEnabled(canChangeName)
        self.txtMnemonic.setText(curve_dict['mnemonic'])
        self.chkMapToY2.setChecked(curve_dict.get('maptoy2', False))
               
        
    def getCurveSetup(self):
        return { 'name': str(self.txtCurveName.text()),
                 'mnemonic': str(self.txtMnemonic.text()),
                 'maptoy2': self.chkMapToY2.isChecked() }

           
class CurveData(QObject):
    def __init__(self, curve_name, maptoy2=False):
        QObject.__init__(self)

        self.setName(curve_name)
        self.maptoy2 = maptoy2
        self.clear()
     
        
    def clear(self):
        self.x = []
        self.y = []
        self.t0 = None
        self.t = None
        
        
    def addPoint(self, y = None, x = None):
        self.emit(PYSIGNAL('addPoint'), (str(self.name()), y, x, False))


    def timeout(self):
        if len(self.y) > 0:
            self.emit(PYSIGNAL('addPoint'), (str(self.name()), self.y[-1], None, True))
       

class GraphWidget(QtBlissGraph):
    def __init__(self, *args):
        QtBlissGraph.__init__(self, *args)

        f = self.parent().font()
        t = qwt.QwtText('')
        t.setFont(f)
        self.setAxisTitle(qwt.QwtPlot.xBottom, t)
        self.setAxisTitle(qwt.QwtPlot.yLeft, t)

        
    def onMouseMoved(self, event):
        pass


    def onMousePressed(self, event):
        pass


    def onMouseReleased(self, event):
        pass
    

class GraphBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.curveData = {}
        self.hardwareObjects = {}
        self.timeAxisX = False
        self.timeAxisElapsedTime = True
        self.windowSize = None
    
        self.defineSlot("clearGraphs", ())
  
        self.addProperty('title', 'string', 'untitled')
        self.addProperty('lineWidth', 'integer', 1)
        self.addProperty('enableGridX', 'boolean', False)
        self.addProperty('enableGridXMin', 'boolean', False)
        self.addProperty('enableGridY', 'boolean', False)
        self.addProperty('enableGridYMin', 'boolean', False)
        #self.addProperty('enableLegend', 'boolean', True)
        self.addProperty('yAxisLabel', 'string', '')
        self.addProperty('y2AxisLabel', 'string', '')
        self.addProperty('xAxisLabel', 'string', '')
        self.addProperty('titleFontSize', 'combo', ('12', '14', '16', '18', '20', '22', '24'), '14')
        self.addProperty('axisTitleFontSize', 'combo', ('6', '8', '10'), '8')
        self.addProperty('timeOnXAxis', 'boolean', 'True')
        self.addProperty('timeElapsedTime', 'boolean', 'True')
        self.addProperty('windowSize', 'integer', '3600')
        self.addProperty('allowSave', 'boolean', False)
        self.getProperty('timeOnXAxis').hidden = True
        self.getProperty('windowSize').hidden = True
        self.getProperty('timeElapsedTime').hidden = True
        self.addProperty('filename', 'string', '', hidden=True)
        
        self.curveSourceSelector = CurveSourceSelector(self)
        self.topPanel = QFrame(self)
        self.curvePanel = QHBox(self.topPanel)
        self.cmdAddCurve = QPushButton('Add curve', self.curvePanel)
        curvePanel = QVBox(self.curvePanel)
        QLabel('Curves :', curvePanel)
        self.lstCurves = QListBox(curvePanel)
        self.cmdEditCurve = QPushButton('Edit curve', self.curvePanel)
        self.cmdRemoveCurve = QPushButton('Remove curve', self.curvePanel)
        self.chkXAxisTimeAxis = QCheckBox('Time on X axis', self.topPanel)
        self.chkElapsedTime = QCheckBox('Elapsed time', self.topPanel)
        self.chkElapsedTime.setChecked(True)
        windowSizePanel = QVBox(self.topPanel)
        QLabel('Window size :', windowSizePanel)
        self.txtWindowSize = QLineEditWithOkCancel(windowSizePanel)
        self.graphPanel = QFrame(self)
        self.graphWidget = GraphWidget(self.graphPanel)
        self.cmdEditCurve.setEnabled(False)
        self.cmdRemoveCurve.setEnabled(False)
        
        QObject.connect(self.cmdAddCurve, SIGNAL('clicked()'), self.cmdAddCurveClicked)
        QObject.connect(self.cmdEditCurve, SIGNAL('clicked()'), self.cmdEditCurveClicked)
        QObject.connect(self.cmdRemoveCurve, SIGNAL('clicked()'), self.cmdRemoveCurveClicked)
        QObject.connect(self.lstCurves, SIGNAL('highlighted(const QString &)'), self.curveSelected)
        QObject.connect(self.chkXAxisTimeAxis, SIGNAL('clicked()'), self.toggleXAxisTimeAxis)
        QObject.connect(self.chkElapsedTime, SIGNAL('clicked()'), self.toggleElapsedTime)
        QObject.connect(self.txtWindowSize, PYSIGNAL('OKClicked'), self.windowSizeChanged)

        self.topPanel.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.topPanel.setLineWidth(1)
        self.topPanel.setMidLineWidth(0)
        self.curvePanel.setSpacing(10)
        self.curvePanel.setMargin(5)
        self.curvePanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.chkXAxisTimeAxis.setChecked(True)
        self.graphPanel.setPaletteBackgroundColor(Qt.white)
        self.graphPanel.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.graphPanel.setLineWidth(1)
        self.graphPanel.setMidLineWidth(0)
        self.graphPanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.savePanel = QHBox(self)
        self.savePanel.setMargin(5)
        self.savePanel.setSpacing(5)
        self.savePanel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cmdSaveData = QToolButton(self.savePanel)
        self.cmdSaveData.setUsesTextLabel(True)
        self.cmdSaveData.setTextLabel("Save data to file")
        QToolTip.add(self.cmdSaveData, "Data will be saved to : %s" % self["filename"])
        self.cmdSaveData.setIconSet(QIconSet(Icons.load("save")))
        if len(self["filename"]) == 0:
            self.cmdSaveData.setEnabled(False)
        self.cmdBrowse = QToolButton(self.savePanel)
        self.cmdBrowse.setUsesTextLabel(True)
        self.cmdBrowse.setTextLabel("Browse")
        self.cmdBrowse.setIconSet(QIconSet(Icons.load("Folder")))
        self.savePanel.hide()

        QObject.connect(self.cmdSaveData, SIGNAL("clicked()"), self.cmdSaveDataClicked)
        QObject.connect(self.cmdBrowse, SIGNAL("clicked()"), self.cmdBrowseClicked)
        
        QVBoxLayout(self, 5, 5)
        self.layout().addWidget(self.topPanel)
        self.layout().addWidget(self.graphPanel)
        self.layout().addWidget(self.savePanel, 0, Qt.AlignVCenter)

        QVBoxLayout(self.topPanel, 5, 5)
        self.topPanel.layout().addWidget(self.curvePanel)
        self.topPanel.layout().addWidget(windowSizePanel)
        self.topPanel.layout().addWidget(self.chkXAxisTimeAxis)
        self.topPanel.layout().addWidget(self.chkElapsedTime)
 
        QHBoxLayout(self.graphPanel)
        self.graphPanel.layout().addWidget(self.graphWidget)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


    def cmdBrowseClicked(self):
        self["filename"] =  QFileDialog.getSaveFileName(os.environ["HOME"],
                                                        "Data file (*.dat *.txt)",
                                                        self,
                                                        "Save file",
                                                        "Choose a filename to save under")


    def cmdSaveDataClicked(self):
        try:
            f = open(self["filename"], "w")
        except:
            logging.getLogger().exception("An error occured while trying to open file %s", self["filename"])
            QMessageBox.warning(self, "Error", "Could not open file %s for writing !" % self["filename"], QMessageBox.Ok)
        else:
            contents = []
            i = 1
            for curve_name, curve_data in self.curveData.items():
                contents.append("\n#S %d %s" % (i, curve_name))
                contents.append("#N 2")
                contents.append("#L  %s  %s" % (self.graphWidget.xlabel() or (self.timeAxisX and "time (s.)" or "X"), self.graphWidget.ylabel() or "Y"))

                for x, y in zip(curve_data.x, curve_data.y):
                    contents.append("%s %s" % (str(x), str(y)))

                contents.append("\n")

            try:
                try:
                    f.write("\n".join(contents))
                except:
                    QMessageBox.warning(self, "Error", "Could not save file to\n%s" % self["filename"], QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Success", "Data have been saved successfully to\n%s" % self["filename"], QMessageBox.Ok)
            finally:
                f.close()
                

    def run(self):        
        self.topPanel.hide()

        for curve_name, curve_data in list(self.curveData.items()):
            self.graphWidget.newcurve(curve_name, curve_data.x, curve_data.y, maptoy2=curve_data.maptoy2)


    def stop(self):
        self.topPanel.show()

        for child in self.topPanel.queryList('QObject'):
            child.blockSignals(False)
        self.topPanel.blockSignals(False)

        for child in self.curveSourceSelector.queryList('QObject'):
            child.blockSignals(False)
        self.curveSourceSelector.blockSignals(False)


    def toggleXAxisTimeAxis(self):
        self.timeAxisX = self.chkXAxisTimeAxis.isChecked()
        self.chkElapsedTime.setEnabled(self.timeAxisX)
              
        for curve_data in self.curveData.values():
            curve_data.clear()
            self.graphWidget.newcurve(str(curve_data.name()), x = [], y = [], maptoy2=curve_data.maptoy2)

        self.setXAxisScale()
            
    def toggleElapsedTime(self):
        self.timeAxisElapsedTime = self.chkElapsedTime.isChecked()
        self.getProperty("timeElapsedTime").setValue(self.timeAxisElapsedTime)

    def setXAxisScale(self):
        if self.timeAxisX:
            self.graphWidget.setx1timescale(True)

            if self.windowSize <= 0:
                self.graphWidget.xAutoScale=True
                #self.graphWidget.setAxisAutoScale(qwt.QwtPlot.xBottom)
            else:
                self.graphWidget.setX1AxisLimits(0-self.windowSize, 0)
                #self.graphWidget.setAxisScale(qwt.QwtPlot.xBottom, 0 - self.windowSize, 0)        
        else:
            self.graphWidget.setx1timescale(False)
            self.graphWidget.xAutoScale=True
            #self.graphWidget.setAxisAutoScale(qwt.QwtPlot.xBottom)
                                            
        self.graphWidget.replot()
        

    def windowSizeChanged(self, size = None):
        try:
            if size is None:
                size = int(str(self.txtWindowSize.text()))
        except ValueError:
            self.txtWindowSize.setText(str(self.windowSize))
        else:
            self.getProperty('windowSize').setValue(size)

            self.windowSize = size

            self.setXAxisScale()
                            
        
    def propertyChanged(self, property, oldValue, newValue):
        if property == 'title':
            self.graphWidget.setTitle(newValue)
        elif property == 'lineWidth':
            self.graphWidget.setactivelinewidth(newValue)
            self.graphWidget.linewidth = newValue
            self.graphWidget.replot()
        elif property == 'enableGridX':
            if newValue:
              self.graphWidget.showGrid()
            else:
              self.graphWidget.hideGrid()
            #self.graphWidget.enableGridX(newValue)
        elif property == 'enableGridXMin':
            if newValue:
              self.graphWidget.showGrid()
            else:
              self.graphWidget.hideGrid()

            #self.graphWidget.enableGridXMin(newValue)
        elif property == 'enableGridY':
            if newValue:
              self.graphWidget.showGrid()
            else:
              self.graphWidget.hideGrid()

            #self.graphWidget.enableGridY(newValue)
        elif property == 'enableGridYMin':
            if newValue:
              self.graphWidget.showGrid()
            else:
              self.graphWidget.hideGrid()

            #self.graphWidget.enableGridYMin(newValue)
        elif property == 'enableLegend':
            self.graphWidget.enableLegend(newValue)
        elif property == 'xAxisLabel':
            self.graphWidget.xlabel(newValue)
        elif property == 'yAxisLabel':
            self.graphWidget.ylabel(newValue)
        elif property == 'y2AxisLabel':
            self.graphWidget.setAxisTitle(qwt.QwtPlot.yRight, newValue)
        elif property == 'titleFontSize':
            t = self.graphWidget.title()
            f = t.font()
            f.setPointSize(int(newValue))
            t.setFont(f)
            self.graphWidget.setTitle(t)
        elif property == 'axisTitleFontSize':
            tx = self.graphWidget.axisTitle(qwt.QwtPlot.xBottom)
            ty = self.graphWidget.axisTitle(qwt.QwtPlot.yLeft)
            ty2 = self.graphWidget.axisTitle(qwt.QwtPlot.yRight)
            fx = tx.font()
            fy = ty.font()
            fy2 = ty2.font()
            size = int(newValue)
            fx.setPointSize(size)
            fy.setPointSize(size)
            fy2.setPointSize(size)
            tx.setFont(fx)
            ty.setFont(fy)
            ty2.setFont(fy2)
            self.graphWidget.setAxisFont(qwt.QwtPlot.xBottom, fx)
            self.graphWidget.setAxisFont(qwt.QwtPlot.yLeft, fy)
            self.graphWidget.setAxisFont(qwt.QwtPlot.yRight, fy2)
            self.graphWidget.setAxisTitle(qwt.QwtPlot.xBottom, tx)
            self.graphWidget.setAxisTitle(qwt.QwtPlot.yLeft, ty)
            self.graphWidget.setAxisTitle(qwt.QwtPlot.yRight, ty2)
        elif property == 'timeOnXAxis':
            self.chkXAxisTimeAxis.setChecked(newValue)
            self.toggleXAxisTimeAxis()
        elif property == 'timeElapsedTime':
            print("timeElapsedTime property value = ", newValue)
            self.chkElapsedTime.setChecked(newValue)
            self.toggleElapsedTime()
        elif property == 'windowSize':
            self.txtWindowSize.setText(str(newValue))
            self.windowSizeChanged(newValue)
        elif property == 'allowSave':
            if newValue:
                self.savePanel.show()
            else:
                self.savePanel.hide()
        elif property == 'filename':
            tp = newValue and "Data will be saved to : %s" % newValue or "Please click 'Browse' to select a filename"
            self.cmdSaveData.setTextLabel("Save data to file")
            QToolTip.add(self.cmdSaveData, tp)
            
            self.cmdSaveData.setEnabled(len(newValue) > 0)
	elif property.startswith('instanceAllow'):
            BlissWidget.propertyChanged(self, property, oldValue, newValue)
        else:
            self.addCurve(newValue)
  
        self.graphWidget.replot()
            

    def cmdAddCurveClicked(self):
        curve_name = 'curve' + str(len(self.curveData))
        while curve_name in self.curveData:
            curve_name = 'curve' + str(len(self.curveData))
                           
        self.curveSourceSelector.setCurve({ 'name':curve_name, 'mnemonic':''})
                
        if self.curveSourceSelector.exec_loop() == QDialog.Accepted:
            curve_setup = self.curveSourceSelector.getCurveSetup()
            print('curve setup', curve_setup)
            
            self.propertyBag.addProperty(curve_setup['name'], '', {})
            self.propertyBag.getProperty(curve_setup['name']).setValue(curve_setup)
            self.propertyBag.getProperty(curve_setup['name']).hidden = True
            self.addCurve(curve_setup)
                

    def addCurve(self, curve_setup_dict):
        self.lstCurves.insertItem(curve_setup_dict['name'])
        self.updateCurve(curve_setup_dict)
                        

    def updateCurve(self, curve_setup_dict):
        curve_name = curve_setup_dict['name']
        mnemonic = curve_setup_dict['mnemonic']
        maptoy2 = curve_setup_dict.get('maptoy2', False)             
             
        if not curve_name in self.graphWidget.curves:
            self.curveData[curve_name] = CurveData(curve_name, maptoy2=maptoy2)
            QObject.connect(self.curveData[curve_name], PYSIGNAL('addPoint'), self.addPoint)
            
        if curve_name in self.hardwareObjects and str(self.hardwareObjects[curve_name].name()) != mnemonic:
            self.disconnect(self.hardwareObjects[curve_name], PYSIGNAL('valueChanged'), self.curveData[curve_name].addPoint)
            self.disconnect(self.hardwareObjects[curve_name], PYSIGNAL('timeout'), self.curveData[curve_name].timeout)
            self.curveData[curve_name].x = []
            self.curveData[curve_name].y = []
            del self.hardwareObjects[curve_name]

        if not curve_name in self.hardwareObjects:
            ho = self.getHardwareObject(mnemonic)

            if ho is not None:
                self.hardwareObjects[curve_name] = ho
            
                self.connect(ho, PYSIGNAL('valueChanged'), self.curveData[curve_name].addPoint)
                self.connect(ho, PYSIGNAL('timeout'), self.curveData[curve_name].timeout)
           
        self.graphWidget.newcurve(curve_name, x = self.curveData[curve_name].x, y = self.curveData[curve_name].y, maptoy2=maptoy2)
    
    def addPoint(self, curve_name, y = None, x = None, timeout = False, replot = True):
        curveData = self.curveData[curve_name]

        if y is None:
            return
        else:
            y = float(y)

        if self.timeAxisX:
            if self.timeAxisElapsedTime: 
              if curveData.t0 is None:
                # 't0' is the starting time (first point added)
                curveData.t0 = time.time()
                curveData.t = curveData.t0
                t = 0
              else:
                # 't' is the time elapsed between the new point and the previous one
                t = time.time() - curveData.t
                curveData.t += t
            else:
              t = int(time.strftime("%S"))+int(time.strftime("%H"))*3600+int(time.strftime("%M"))*60
              curveData.t = t

            if self.windowSize > 0:
                x = 0
                
                n0 = len(curveData.x)
                curveData.x = [_f for _f in [x + self.windowSize > 0 and x - t for x in curveData.x] if _f]
                n = len(curveData.x)
                
                if n0 > n:
                    curveData.y = curveData.y[n0 - n:]
            else:
                if self.timeAxisElapsedTime:
                  x = curveData.t - curveData.t0
                else:
                  x = curveData.t

        elif x is not None:
            x = float(x)
        else:
            if timeout:
                return
            
            if len(curveData.x) > 0:
                x = curveData.x[-1] + 1
            else:
                x = 0
                                  
        curveData.x.append(x)  
        curveData.y.append(y)

        if self.windowSize:
            if not self.timeAxisX and len(curveData.y) == self.windowSize:
                del curveData.y[0]
                del curveData.x[0]

        if replot is True:
            if self.isRunning():            
                self.graphWidget.newcurve(curve_name, curveData.x,  curveData.y, maptoy2=curveData.maptoy2)
                self.graphWidget.replot()                
        
                                                   

    def curveSelected(self, curve_name):
        self.cmdEditCurve.setEnabled(True)
        self.cmdRemoveCurve.setEnabled(True)
    
        
    def cmdEditCurveClicked(self):
        selected_curve = str(self.lstCurves.currentText())
        
        self.curveSourceSelector.setCurve(self.propertyBag[selected_curve], canChangeName = False)

        if self.curveSourceSelector.exec_loop() == QDialog.Accepted:
            self.propertyBag.getProperty(selected_curve).setValue(self.curveSourceSelector.getCurveSetup())
            self.updateCurve(self.curveSourceSelector.getCurveSetup())
        

    def clearGraphs(self):
        for i in range(self.lstCurves.count()):
          curve_name = str(self.lstCurves.text(i))
          self.curveData[curve_name].clear()
          self.graphWidget.newcurve(curve_name, x=[], y=[])

          
          
    def removeCurve(self, pCurveName):
        
        pCurveName = str(pCurveName)
        
        try:
            del self.curveData[pCurveName]  # verify why inside try
            
            del self.hardwareObjects[pCurveName]
        except KeyError:
            #it can happen if no hardware object has been assigned
            pass
        
        self.graphWidget.newcurve(pCurveName, x = [], y = []) #delete curve          




    def cmdRemoveCurveClicked(self):
        selected_curve = str(self.lstCurves.currentText())

        self.lstCurves.removeItem(self.lstCurves.currentItem())
        
        del self.propertyBag.properties[selected_curve]
        del self.curveData[selected_curve]
        try:
            del self.hardwareObjects[selected_curve]
        except KeyError:
            #it can happen if no hardware object has been assigned
            pass

        self.graphWidget.newcurve(selected_curve, x = [], y = []) #delete curve
        


