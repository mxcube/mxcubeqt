#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
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
import numpy as np

pymca_imported = False
try:
    if QtImport.qt_variant == "PyQt5":
        from PyMca5.PyMca import McaAdvancedFit
        from PyMca5.PyMca import ConfigDict
    else:
        from PyMca import McaAdvancedFit
        from PyMca import ConfigDict
    pymca_imported = True
except BaseException:
    pass

if not pymca_imported:
    from gui.widgets.matplot_widget import TwoAxisPlotWidget

from gui.utils import QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class McaSpectrumWidget(BaseWidget):
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self.define_slot("set_data", ())

        if pymca_imported:
            self.mcafit_widget = McaAdvancedFit.McaAdvancedFit(self)
            self.mcafit_widget.dismissButton.hide()
        else:
            self.mcafit_widget = TwoAxisPlotWidget(self)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.mcafit_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

    def set_data(self, data, calib, config):
        try:
            configured = False
            if os.path.exists(config.get("file", "")) and pymca_imported:
                self._configure(config)
                configured = True
            data = np.array(data)
            x = np.array(data[:, 0]).astype(np.float)
            y = np.array(data[:, 1]).astype(np.float)
            xmin = float(config["min"])
            xmax = float(config["max"])
            # self.mcafit_widget.refreshWidgets()
            calib = np.ravel(calib).tolist()
            """kw = {}
            kw.update(config)
            kw['xmin'] = xmin
            kw['xmax'] = xmax
            kw['calibration'] = calib"""
            self.mcafit_widget.setdata(x, y)
            if pymca_imported:
                # elf.mcafit.setdata(x, y, **kw)# xmin=xmin, xmax=xmax,
                # calibration=calib)
                self.mcafit_widget._energyAxis = False
                self.mcafit_widget.toggleEnergyAxis()
                self.mcafit_widget.setdata(x, y)
            # result = self._fit()
            # pyarch file name and directory
            pf = config["legend"].split(".")
            pd = pf[0].split("/")
            outfile = pd[-1]
            outdir = config["htmldir"]
            sourcename = config["legend"]

            if pymca_imported:
                result = self._fit()
                if configured:
                    report = McaAdvancedFit.QtMcaAdvancedFitReport.QtMcaAdvancedFitReport(
                        None,
                        outfile=outfile,
                        outdir=outdir,
                        fitresult=result,
                        sourcename=sourcename,
                        plotdict={"logy": False},
                        table=2,
                    )

                    text = report.getText()
                    report.writeReport(text=text)

        except BaseException:
            logging.getLogger("HWR").exception("McaSpectrumWidget: problem fitting")

    def _fit(self):
        return self.mcafit_widget.fit()

    def _configure(self, config):
        d = ConfigDict.ConfigDict()
        d.read(config["file"])
        if "concentrations" not in d:
            d["concentrations"] = {}
        if "attenuators" not in d:
            d["attenuators"] = {}
            d["attenuators"]["Matrix"] = [1, "Water", 1.0, 0.01, 45.0, 45.0]
        if "flux" in config:
            d["concentrations"]["flux"] = float(config["flux"])
        if "time" in config:
            d["concentrations"]["time"] = float(config["time"])
        self.mcafit_widget.mcafit.configure(d)

    def clear(self):
        # TODO make with clear
        x = np.array([0]).astype(np.float)
        y = np.array([0]).astype(np.float)
        self.mcafit_widget.setdata(x, y)
