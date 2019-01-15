import qt
import time
import gevent
from datetime import timedelta
from BlissFramework.BaseComponents import BlissWidget


class ProgressBarBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.collect_hwobj = None

        self.addProperty("mnemonic", "string", "")
        self.addProperty("appearance", "combo", ("simple", "normal"), "normal")
        self.addProperty("title", "string", "")
        self.addProperty("timeFormat", "string", "%H:%M:%S")

        self.executing = None
        self.time_total_sec = 0
        self.time_remaining_sec = 0
        self.time_format = None
        self.progress_task = None

        self.container_hbox = qt.QHGroupBox(self)
        self.container_hbox.setInsideMargin(4)
        self.container_hbox.setInsideSpacing(2)

        self.time_total_label = qt.QLabel("Total:", self.container_hbox)
        self.time_total_value_label = qt.QLabel("??:??:??", self.container_hbox)
        self.progressBar = qt.QProgressBar(self.container_hbox)
        self.progressBar.setCenterIndicator(True)
        self.time_remaining_label = qt.QLabel("Remaining:", self.container_hbox)
        self.time_remaining_value_label = qt.QLabel("??:??:??", self.container_hbox)

        qt.QVBoxLayout(self)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Fixed)
        self.layout().addWidget(self.container_hbox)

        self.setEnabled(False)
        self.instanceSynchronize("")

    def run(self):
        self.reset_progress()

    def stop_progress(self, *args):
        self.setEnabled(False)

    def start_progress(self, *args):
        if not self.progress_task:
            self.setEnabled(True)
            self.progress_task = gevent.spawn(self.execute_progress)

    def reset_progress(self):
        self.progressBar.reset()
        self.time_total_value_label.setText(str(timedelta(seconds=0)))
        self.time_remaining_value_label.setText(str(timedelta(seconds=0)))
        if self.progress_task is not None:
            self.progress_task.kill()
        self.total_time_task = None
        self.setEnabled(False)

    def set_progress_total_time(self, number_of_frames, exposure_time):
        self.reset_progress()
        self.time_total_sec = int(number_of_frames * exposure_time)
        self.progressBar.setTotalSteps(self.time_total_sec)
        self.time_remaining_sec = self.time_total_sec
        self.time_total_value_label.setText(str(timedelta(seconds=self.time_total_sec)))
        self.setEnabled(True)

    def execute_progress(self):
        while self.time_remaining_sec > -1:
            self.progressBar.setProgress(self.time_total_sec - self.time_remaining_sec)
            self.time_remaining_value_label.setText(
                str(timedelta(seconds=int(self.time_remaining_sec)))
            )
            self.time_remaining_sec = self.time_remaining_sec - 1
            time.sleep(1)
        self.setEnabled(False)
        self.progress_task = None

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == "appearance":
            if newValue == "simple":
                self.container_hbox.setFrameShape(self.container_hbox.NoFrame)
                self.container_hbox.setInsideMargin(0)
                self.container_hbox.setInsideSpacing(0)
                self.time_total_label.hide()
                self.time_total_value_label.hide()
                self.time_remaining_label.hide()
                self.time_remaining_value_label.hide()
            elif newValue == "normal":
                self.container_hbox.setFrameShape(self.container_hbox.GroupBoxPanel)
                self.container_hbox.setInsideMargin(4)
                self.container_hbox.setInsideSpacing(2)
                self.time_total_label.show()
                self.time_total_value_label.show()
                self.time_remaining_label.show()
                self.time_remaining_value_label.show()
        elif propertyName == "title":
            if newValue != "":
                self.container_hbox.setTitle(newValue)
                self.updateGeometry()
        elif propertyName == "timeFormat":
            self.time_format = newValue
        elif propertyName == "mnemonic":
            if self.collect_hwobj is not None:
                self.disconnect(
                    self.collect_hwobj,
                    qt.PYSIGNAL("collectNumberOfFrames"),
                    self.set_progress_total_time,
                )
                self.disconnect(
                    self.collect_hwobj,
                    qt.PYSIGNAL("collectImageTaken"),
                    self.start_progress,
                )
                self.disconnect(
                    self.collect_hwobj, qt.PYSIGNAL("collectEnded"), self.stop_progress
                )
            self.collect_hwobj = self.getHardwareObject(newValue)
            if self.collect_hwobj is not None:
                self.connect(
                    self.collect_hwobj,
                    qt.PYSIGNAL("collectNumberOfFrames"),
                    self.set_progress_total_time,
                )
                self.connect(
                    self.collect_hwobj,
                    qt.PYSIGNAL("collectImageTaken"),
                    self.start_progress,
                )
                self.connect(
                    self.collect_hwobj, qt.PYSIGNAL("collectEnded"), self.stop_progress
                )
        else:
            BlissWidget.propertyChanged(self, propertyName, oldValue, newValue)
