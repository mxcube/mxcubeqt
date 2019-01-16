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
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.


import logging
import numpy.oldnumeric as Numeric

import QtImport

from PyMca import McaAdvancedFit
from PyMca import ConfigDict

from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class McaSpectrumBrick(BaseWidget):

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        self.defineSlot("setData", ())

        self.mcafit = McaAdvancedFit.McaAdvancedFit(self)
        self.mcafit.dismissButton.hide()

        # Layout --------------------------------------------------------------
        main_layout = QtImport.QVBoxLayout(self)
        main_layout.addWidget(self.mcafit)
        # main_layout.addWidget(self.scan_plot_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def setData(self, data, calib, config):
        try:
            configured = False
            if config.get("file", None):
                self._configure(config)
                configured = True
            data = Numeric.array(data)
            x = Numeric.array(data[:, 0]).astype(Numeric.Float)
            y = Numeric.array(data[:, 1]).astype(Numeric.Float)
            xmin = float(config["min"])
            xmax = float(config["max"])
            # self.mcafit.refreshWidgets()
            calib = Numeric.ravel(calib).tolist()
            """kw = {}
            kw.update(config)
            kw['xmin'] = xmin
            kw['xmax'] = xmax
            kw['calibration'] = calib"""
            self.mcafit.setdata(x, y)
            # elf.mcafit.setdata(x, y, **kw)# xmin=xmin, xmax=xmax, calibration=calib)
            self.mcafit._energyAxis = False
            self.mcafit.toggleEnergyAxis()
            # result = self._fit()
            # pyarch file name and directory
            pf = config["legend"].split(".")
            pd = pf[0].split("/")
            outfile = pd[-1]
            outdir = config["htmldir"]
            sourcename = config["legend"]

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
            logging.getLogger().exception(
                "McaSpectrumBrick: problem fitting %s %s %s"
                % (str(data), str(calib), str(config))
            )

    def _fit(self):
        return self.mcafit.fit()

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
        self.mcafit.mcafit.configure(d)

    def clear(self):
        x = Numeric.array([0]).astype(Numeric.Float)
        y = Numeric.array([0]).astype(Numeric.Float)
        self.mcafit.setdata(x, y)
