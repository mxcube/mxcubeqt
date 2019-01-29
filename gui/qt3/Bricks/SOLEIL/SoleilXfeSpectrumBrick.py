from XfeSpectrumBrick import XfeSpectrumBrick
import logging

from qt import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

import numpy
import shutil

import time
import os
import traceback

__category__ = 'SOLEIL'


class SoleilXfeSpectrumBrick(XfeSpectrumBrick):

    def __init__(self, *args):

        XfeSpectrumBrick.__init__(self, *args)

        self.parametersBox.setChecked(True)

    def spectrumFinished(self, mca_data, calib, config):

        a = str(self.directoryInput.text()).split(os.path.sep)
        print 'a', a
        dirctr = str(self.directoryInput.text())  # let's have string instead of QString
        print 'self.directoryInput.text()', self.directoryInput.text()
        if dirctr[-1] == '/':
            a_dir = dirctr[:-1]
        else:
            a_dir = dirctr

        #a = str(self.directoryInput.text()).split(os.path.sep)
        # suffix_path=os.path.join(*a[4:])
        # if 'inhouse' in a :
            #a_dir = os.path.join('/data/pyarch/', a[2], suffix_path)
        # else:
            #a_dir = os.path.join('/data/pyarch/',a[4],a[3],*a[5:])
        # if a_dir[-1]!=os.path.sep:
            # a_dir+=os.path.sep
        print "a_dir --------------------------->", a_dir

        if not os.path.exists(os.path.dirname(a_dir)):
            os.makedirs(os.path.dirname(a_dir))

        filename_pattern = os.path.join(a_dir, "%s_%s_%%02d" % (
            str(self.prefixInput.text()), time.strftime("%d_%b_%Y")))
        filename_pattern = os.path.extsep.join((filename_pattern, "png"))
        filename = filename_pattern % 1

        i = 2
        while os.path.isfile(filename):
            filename = filename_pattern % i
            i = i + 1
        try:
            a = float(calib[0])
            b = float(calib[1])
            c = float(calib[2])
        except BaseException:
            a = 0
            b = 1
            c = 0
        calibrated_data = []
        for line in mca_data:
            channel = line[0]
            counts = line[1]
            energy = a + b * channel + c * channel * channel
            calibrated_line = [energy, counts]
            calibrated_data.append(calibrated_line)
        calibrated_array = numpy.array(calibrated_data)

        fig = Figure(figsize=(15, 11))
        ax = fig.add_subplot(111)
        ax.set_title(filename)
        ax.grid(True)
        #ax.plot(*(zip(*mca_data)), **{"color":'black'})
        ax.plot(*(zip(*calibrated_array)), **{"color": 'black'})
        #ax.set_xlabel("MCA channel")
        #ax.set_ylabel("MCA counts")
        ax.set_xlabel("Energy")
        ax.set_ylabel("Counts")
        canvas = FigureCanvasAgg(fig)
        logging.getLogger().info("Rendering spectrum to PNG file : %s", filename)
        canvas.print_figure(filename, dpi=80)
        logging.getLogger().debug("Copying PNG file to: %s", a_dir)
        #shutil.copy (filename, a_dir)
        try:
            shutil.copy(filename, str(a_dir) + '/')
            logging.getLogger().debug("Copying .fit file to: %s", a_dir)
        except BaseException:
            print 'Problem copying file ', filename, 'to ', a_dir
            logging.getLogger().debug("Problem copying .fit file to: %s", a_dir)

        logging.getLogger().debug("Copying .fit file to: %s", a_dir)
        # tmpname=filename.split(".")

        color = XfeSpectrumBrick.STATES['ok']
        self.statusBox.setTitle("Xfe spectrum status")

        config['max'] = 'max_user'  # config['max_user']
        config['htmldir'] = a_dir
        try:
            self.emit(PYSIGNAL("xfeSpectrumDone"), (mca_data, calib, config))
        except BaseException:
            logging.getLogger().exception("XfeSpectrumBrick: problem updating embedded PyMCA")
            print traceback.print_exc
            traceback.print_exc
        self.spectrumStatus.setPaletteBackgroundColor(QColor(color))

        self.startSpectrumButton.commandDone()
        self.emit(PYSIGNAL("xfeSpectrumRun"), (False,))
        self.parametersBox.setEnabled(True)
