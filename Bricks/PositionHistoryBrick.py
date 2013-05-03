from BlissFramework import BaseComponents
from BlissFramework import Icons
from qt import *
from Qub.Objects.QubDrawingManager import QubPointDrawingMgr, Qub2PointSurfaceDrawingMgr, QubAddDrawing
from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget
import position_history_widget
import math
import numpy
import logging
import sys

__category__ = 'mxCuBE'


class PositionHistoryBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)
        
        reload(position_history_widget)

        self.points = []
        self.centred_positions = {}

        self.defineSlot("tree_selection_changed", ())
        self.defineSlot("new_centred_position", ())
        self.defineSignal("getView", ())
        self.defineSignal("add_data_collection", ())
        self.defineSignal("hideParametersTab", ())
        self.defineSignal("hideSampleCentringTab", ())
        self.defineSignal("get_selected_sample", ())
        
        self.addProperty("diffractometer", "string", "")

        self.position_history = position_history_widget.\
            PositionHistoryBrickWidget(self)
        
        self.position_history.create_dc_cb = self.add_dc
        self.position_history.new_position_cb = self.new_position
        self.position_history.position_selected_cb = self.centred_position_selected
        self.position_history.delete_centrings_cb = self.delete_centrings

        QVBoxLayout(self)
        self.layout().addWidget(self.position_history)
            
            
    def run(self):
        d = {}
        self.emit(PYSIGNAL("getView"), (d, ))
        self.__drawing = d.get('drawing',None)
        self.__view = d.get('view',None)
   

    def new_position(self, point):
        point = self.diffractometer.motor_positions_to_screen(point)

        draw_point, _ = QubAddDrawing(self.__drawing, QubPointDrawingMgr, QubCanvasTarget)

        draw_point.show()
        draw_point.setPoint(point[0], point[1])
        draw_point.setColor(Qt.yellow)
        self.points.append(draw_point)

        self.centred_positions[draw_point] = self.diffractometer.getPositions()


    def tree_selection_changed(self, item):
        pass


    def centred_position_selected(self, selected_positions_idx):
        selected_points = [self.points[idx] for idx in selected_positions_idx]
        if selected_points:
            highlighted_pen = QPen(self.points[0]._drawingObjects[0].pen())
            highlighted_pen.setWidth(2)
            normal_pen = QPen(highlighted_pen)
            normal_pen.setWidth(1)
            for point in self.points:
                if point in selected_points:
                    point.setPen(highlighted_pen)
                else:
                    point.setPen(normal_pen)


    def delete_centrings(self, positions_indexes):
        for i in range(len(positions_indexes)):
            idx = positions_indexes[i]-i
            p = self.points[idx]
            del self.centred_positions[p]
            p.hide()
            self.points.pop(idx)
            

    def add_dc(self):
        points = self.position_history.selected_points()
        collection_type = self.position_history.get_collection_type()

        selected_sample = { "sample_item": None }
        self.emit(PYSIGNAL("get_selected_sample"), (selected_sample, ))
        selected_sample = selected_sample["sample_item"]
        
        if selected_sample is None:
            QMessageBox.information(self,
                                    "Select centred positions",
                                    "Please select a sample",
                                    "OK")
        elif len(points) == 0:
            QMessageBox.information(self,
                                    "Select centred positions",
                                    "Please select one or more centred positions",
                                    "OK")
        else:
            dc_parameters = dc_parameter_factory()
            dc_parameters['positions'] = points
            #self.emit(PYSIGNAL("hideParametersTab"), (False,))
            #self.emit(PYSIGNAL("hideSampleCentringTab"), (True,))
            self.emit(PYSIGNAL("add_data_collection"), (dc_parameters, collection_type))


    def new_centred_position(self, state, centring_status):
        self.position_history.add_centred_position(state, centring_status)
        

    def diffractometer_changed(self):
        if self.diffractometer.isReady():
            for point in self.points:
                new_x, new_y = self.diffractometer.motor_positions_to_screen(self.centred_positions[point])
                point.move(new_x, new_y)
                point.show()
        else:
            for point in self.points:
                point.hide()

            
    def propertyChanged(self, property, old_value, new_value):
        if property == "diffractometer":
             self.diffractometer = self.getHardwareObject(new_value)
             self.diffractometer.connect("minidiffStateChanged", self.diffractometer_changed)


def dc_parameter_factory():
    return { 'prefix': ['Prefix', 'prefix'],
             'run_number' : ['Run Number', '1'],
             'template' : ['Template', '#prefix_1_####.mccd'],
             'first_image' : ['First image #:', '1'],
             'num_images' : ['Number of images', '1'],
             'osc_start' : ['Oscillation start', '0.00'],
             'osc_range' : ['Oscillation range', '1.00'],
             'exp_time' : ['Exposure time(s)', '1.0'],
             'num_passes' : ['Number of passes', '1'],
             'comments' : ['Comments', 'comments'],
             'path' : ['Path', '/some/nice/path'],
             'positions': []}
