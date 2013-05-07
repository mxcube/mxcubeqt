import qt
import queue_model

from BlissFramework import BaseComponents
from widgets.crystal_widget_layout import CrystalWidgetLayout
from widgets.sample_info_widget_layout import SampleInfoWidgetLayout
from widgets.widget_utils import DataModelInputBinder

__category__ = 'mxCuBE_v3'

class SampleDetailsBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        #
        # Data attributes
        #
        self.sample = queue_model.Sample(None)
        self.crystal = self.sample.crystals[0]
        self.sample_mib = DataModelInputBinder(self.sample)
        self.crystal_mib = DataModelInputBinder(self.crystal)
        
        #
        # Qt - Signals/Slots
        #
        self.defineSlot("populate_sample_details", ({}))

        #
        # Layout
        #
        main_layout = qt.QHBoxLayout(self, 11, 15, "main_layout")
        self.crystal_widget = CrystalWidgetLayout(self)
        self.sample_info_widget = SampleInfoWidgetLayout(self)
        main_layout.addWidget(self.sample_info_widget)
        main_layout.addWidget(self.crystal_widget)
        main_layout.addStretch(10)

        self.crystal_mib.bind_value_update('space_group',
                                           self.crystal_widget.space_group_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('protein_acronym',
                                           self.crystal_widget.protein_acronym_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_a',
                                           self.crystal_widget.a_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_alpha',
                                           self.crystal_widget.alpha_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_b',
                                           self.crystal_widget.b_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_beta',
                                           self.crystal_widget.beta_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_c',
                                           self.crystal_widget.c_value_label,
                                           str,
                                           None)

        self.crystal_mib.bind_value_update('cell_gamma',
                                           self.crystal_widget.gamma_value_label,
                                           str,
                                           None)

        self.sample_mib.bind_value_update('name',
                                          self.sample_info_widget.name_value_label,
                                          str,
                                          None)
        

        self.sample_mib.bind_value_update('code',
                                          self.sample_info_widget.data_matrix_value_label,
                                          str,
                                          None)


        self.sample_mib.bind_value_update('holder_length',
                                          self.sample_info_widget.holder_length_value_label,
                                          str,
                                          None)


        self.sample_mib.bind_value_update('lims_sample_location',
                                          self.sample_info_widget.sample_location_value_label,
                                          str,
                                          None)


        self.sample_mib.bind_value_update('lims_container_location',
                                          self.sample_info_widget.basket_location_value_label,
                                          str,
                                          None)



    def populate_sample_details(self, sample):
        self.sample = sample
        self.crystal = sample.crystals[0]
        self.crystal_mib.set_model(self.crystal)
        self.sample_mib.set_model(sample)
        
