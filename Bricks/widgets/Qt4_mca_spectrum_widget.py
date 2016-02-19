#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""
[Name] McaSpectrumWidget

[Description]
The McaSpectrumWidget allows to display Mca Spectrum obtained in SPEC.
If configured, it will take into account the energy calibration factors and
the fit configuration file well as 

[Properties]

[Signals]

[Slots]
-------------------------------------------------------------
| name     | arguments | description
-------------------------------------------------------------
| setData  | data      | numeric array (x, y)
           | calib     | dictionary with the calibration factors (a,b,c)
           | config    | dictionary with the fit parameters



[HardwareObjects]

"""
import os
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

import numpy.oldnumeric as Numeric
from PyMca import McaAdvancedFit
from PyMca import ConfigDict

from BlissFramework.Qt4_BaseComponents import BlissWidget


class McaSpectrumWidget(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.defineSlot('set_data',())
       
        self.mcafit_widget = McaAdvancedFit.McaAdvancedFit(self)
        self.mcafit_widget.dismissButton.hide()
       
        _main_vlayout = QtGui.QVBoxLayout(self)
        _main_vlayout.addWidget(self.mcafit_widget)  
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def set_data(self, data, calib, config):
        try:
            configured = False
            if os.path.exists(config.get("file", "")):
                self._configure(config)
                configured = True
            data = Numeric.array(data)
            x = Numeric.array(data[:,0]).astype(Numeric.Float)
            y = Numeric.array(data[:,1]).astype(Numeric.Float)
            xmin = float(config["min"])
            xmax = float(config["max"])
            #self.mcafit_widget.refreshWidgets()
            calib = Numeric.ravel(calib).tolist()
            """kw = {}
            kw.update(config)
            kw['xmin'] = xmin
            kw['xmax'] = xmax
            kw['calibration'] = calib"""
            self.mcafit_widget.setdata(x, y)
            #elf.mcafit.setdata(x, y, **kw)# xmin=xmin, xmax=xmax, calibration=calib)
            self.mcafit_widget._energyAxis = False
            self.mcafit_widget.toggleEnergyAxis()
            #result = self._fit()
            #pyarch file name and directory
            pf = config["legend"].split(".")
            pd = pf[0].split("/")
            outfile = pd[-1]
            outdir = config['htmldir']
            sourcename = config['legend']

            result = self._fit()
            if configured:
                report = McaAdvancedFit.QtMcaAdvancedFitReport.\
                     QtMcaAdvancedFitReport(None, outfile=outfile, outdir=outdir,
                     fitresult=result, sourcename=sourcename, 
                     plotdict={'logy':False}, table=2)

                text = report.getText()
                report.writeReport(text=text)
  
        except:
            logging.getLogger().exception("McaSpectrumWidget: problem fitting %s %s %s" % \
                                          (str(data), str(calib), str(config)))

    def _fit(self):
        return self.mcafit_widget.fit()

    def _configure(self,config):
        d = ConfigDict.ConfigDict()
        d.read(config["file"])
        if not d.has_key('concentrations'):
            d['concentrations']= {}
        if not d.has_key('attenuators'):
            d['attenuators']= {}
            d['attenuators']['Matrix'] = [1, 'Water', 1.0, 0.01, 45.0, 45.0]
        if config.has_key('flux'):
            d['concentrations']['flux'] = float(config['flux'])
        if config.has_key('time'):
            d['concentrations']['time'] = float(config['time'])
        self.mcafit_widget.mcafit.configure(d)

    def clear(self):
        #TODO make with clear
        x = Numeric.array([0]).astype(Numeric.Float)
        y = Numeric.array([0]).astype(Numeric.Float)
        self.mcafit_widget.setdata(x, y)
