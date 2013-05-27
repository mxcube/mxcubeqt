import os
import array
import queue_model

from qt import *
from qttable import QTable, QTableItem

from widgets.reference_image_widget import ReferenceImageWidget
from widgets.char_type_widget import CharTypeWidget
from widgets.optimisation_parameters_widget_layout\
    import OptimisationParametersWidgetLayout
from widgets.radiation_damage_model_widget_layout\
    import RadiationDamageModelWidgetLayout
from widgets.acquisition_widget import AcquisitionWidget
from widgets.diffraction_plan_widget_layout\
    import DiffractionPlanWidgetLayout
from widgets.snapshot_widget_layout import SnapshotWidgetLayout
from widgets.widget_utils import DataModelInputBinder
from widgets.vertical_crystal_dimension_widget_layout\
    import VerticalCrystalDimensionWidgetLayout

from queue_model import COLLECTION_ORIGIN
from BlissFramework.Utils import widget_colors

class CharParametersWidget(QWidget):
    def __init__(self, parent = None, name = "parameter_widget"):
        QWidget.__init__(self, parent, name)

        #
        # Private members
        #
        self._data_collection = None
        self._char_params = queue_model.CharacterisationParameters()
        self._char_params_mib = DataModelInputBinder(self._char_params)
        self.previous_energy = None
        
        self.add_dc_cb = None

        self.char_type_widget = CharTypeWidget(self)
        self.routine_dc_widget = self.char_type_widget.routine_dc_page
        self.sad_widget = self.char_type_widget.sad_page
        self.rad_dmg_char_widget = self.char_type_widget.rad_damage_page
        self.reference_img_widget = ReferenceImageWidget(self)
        self.acq_widget = self.reference_img_widget.acq_widget
        self.path_widget = self.reference_img_widget.path_widget
        self.opt_parameters_widget = OptimisationParametersWidgetLayout(self)
        self.rad_dmg_widget = RadiationDamageModelWidgetLayout(self)
        self.position_widget = SnapshotWidgetLayout(self)
        self.vertical_dimension_widget = VerticalCrystalDimensionWidgetLayout(self)

        # Fix the widths of the widgets to make the layout look nicer,
        # and beacuse the qt layout engine is so tremendosly good.
        self.opt_parameters_widget.setFixedWidth(600)
        self.reference_img_widget.setFixedWidth(772)

        #
        # Layout
        #
        v_layout = QVBoxLayout(self, 11, 15, "main_layout")
        rone_hlayout = QHBoxLayout(v_layout, 15, "rone" )
        rone_cone_vlayout = QVBoxLayout(rone_hlayout, 15, "rone_cone")
        rtwo_hlayout = QHBoxLayout(v_layout, 15, "rtwo")
        rthree_hlayout =QHBoxLayout(v_layout, 15, "rtwo")

        rone_hlayout.addWidget(self.position_widget)
        rone_cone_vlayout.addWidget(self.reference_img_widget)        
        rone_hlayout.addStretch()
        
        rtwo_hlayout.addWidget(self.char_type_widget)
        rtwo_hlayout.addWidget(self.opt_parameters_widget)
        rtwo_hlayout.addStretch(10)
        v_layout.addStretch(10)

        rthree_hlayout.addWidget(self.rad_dmg_widget)
        rthree_hlayout.addWidget(self.vertical_dimension_widget)
        rthree_hlayout.addStretch(10)
        v_layout.addStretch(10)


        #
        # Widget logic
        # 
        self.toggle_permitted_range(self.\
            opt_parameters_widget.permitted_range_cbx.isOn())
        QObject.connect(self.opt_parameters_widget.permitted_range_cbx,
                        SIGNAL("toggled(bool)"),
                        self.toggle_permitted_range)


        self._char_params_mib.bind_value_update('min_dose',
                                                 self.routine_dc_widget.dose_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('min_time',
                                                 self.routine_dc_widget.time_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))


        self._char_params_mib.bind_value_update('use_min_dose',
                                                 self.routine_dc_widget.min_dose_radio,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('use_min_time',
                                                 self.routine_dc_widget.min_time_radio,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('account_rad_damage',
                                                 self.routine_dc_widget.radiation_damage_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('auto_res',
                                                 self.sad_widget.automatic_resolution_radio,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('opt_sad',
                                                 self.sad_widget.optimal_sad_radio,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('determine_rad_params',
                                                 self.rad_dmg_char_widget.rad_damage_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('burn_osc_start',
                                                 self.rad_dmg_char_widget.burn_osc_start_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('burn_osc_interval',
                                                 self.rad_dmg_char_widget.burn_osc_interval_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('use_aimed_resolution',
                                                 self.opt_parameters_widget.maximum_res_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('use_aimed_multiplicity',
                                                 self.opt_parameters_widget.aimed_mult_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('aimed_resolution',
                                                 self.opt_parameters_widget.maximum_res_ledit,
                                                 float,
                                                 QDoubleValidator(0.01, 1000, 2, self))

        self._char_params_mib.bind_value_update('aimed_multiplicity',
                                                 self.opt_parameters_widget.aimed_mult_ledit,
                                                 float,
                                                 QDoubleValidator(0.01, 1000, 2, self))

        self._char_params_mib.bind_value_update('aimed_i_sigma',
                                                 self.opt_parameters_widget.i_over_sigma_ledit,
                                                 float,
                                                 QDoubleValidator(0.01, 1000, 2, self))

        self._char_params_mib.bind_value_update('aimed_completness',
                                                 self.opt_parameters_widget.aimed_comp_ledit,
                                                 float,
                                                 QDoubleValidator(0.01, 1000, 2, self))
        
        self._char_params_mib.bind_value_update('strategy_complexity',
                                                 self.opt_parameters_widget.start_comp_cbox,
                                                 int,
                                                 None)

        self._char_params_mib.bind_value_update('use_permitted_rotation',
                                                 self.opt_parameters_widget.permitted_range_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('permitted_phi_start',
                                                 self.opt_parameters_widget.phi_start_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('permitted_phi_end',
                                                 self.opt_parameters_widget.phi_end_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('low_res_pass_strat',
                                                 self.opt_parameters_widget.low_res_pass_cbx,
                                                 bool,
                                                 None)

        self._char_params_mib.bind_value_update('rad_suscept',
                                                 self.rad_dmg_widget.sensetivity_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('beta',
                                                 self.rad_dmg_widget.beta_over_gray_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('gamma',
                                                 self.rad_dmg_widget.gamma_over_gray_ledit,
                                                 float,
                                                 QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('max_crystal_vdim',
                                            self.vertical_dimension_widget.max_vdim_ledit,
                                            float,
                                            QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('min_crystal_vdim',
                                            self.vertical_dimension_widget.min_vdim_ledit,
                                            float,
                                            QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('min_crystal_vphi',
                                            self.vertical_dimension_widget.min_vphi_ledit,
                                            float,
                                            QDoubleValidator(0.0, 1000, 2, self))

        self._char_params_mib.bind_value_update('max_crystal_vphi',
                                            self.vertical_dimension_widget.max_vphi_ledit,
                                            float,
                                            QDoubleValidator(0.0, 1000, 2, self))


        self._char_params_mib.bind_value_update('space_group',
                                                self.vertical_dimension_widget.space_group_ledit,
                                                str,
                                                None)


        QObject.connect(self.char_type_widget.charact_type_tbox,
                        SIGNAL("currentChanged(int)"),
                        self.update_char_type)

        QObject.connect(self.rad_dmg_char_widget.rad_damage_cbx,
                        SIGNAL("toggled(bool)"),
                        self.enable_opt_parameters_widget)

        QObject.connect(self.opt_parameters_widget.maximum_res_cbx,
                        SIGNAL("toggled(bool)"),
                        self.enable_maximum_res_ledit)

        QObject.connect(self.opt_parameters_widget.aimed_mult_cbx,
                        SIGNAL("toggled(bool)"),
                        self.enable_aimed_mult_ledit)


    def enable_aimed_mult_ledit(self, state):
        self.opt_parameters_widget.aimed_mult_ledit.setEnabled(state)


    def enable_maximum_res_ledit(self, state):
        self.opt_parameters_widget.maximum_res_ledit.setEnabled(state)


    def update_char_type(self, index):
        self._char_params.experiment_type = index
    

    def toggle_permitted_range(self, status):
        self.opt_parameters_widget.phi_start_ledit.setEnabled(status)
        self.opt_parameters_widget.phi_end_ledit.setEnabled(status)


    def enable_opt_parameters_widget(self, state):
        self.opt_parameters_widget.setEnabled(not state)


    def populate_parameter_widget(self, char):
        self._data_collection = char.reference_image_collection
        self._char_params = char.characterisation_parameters
        self._char_params_mib.set_model(char.characterisation_parameters)
       
        self.acq_widget.update_data_model(char.reference_image_collection.\
                                          acquisitions[0].acquisition_parameters,
                                          char.reference_image_collection.\
                                          acquisitions[0].path_template)
        
        self.path_widget.update_data_model(char.reference_image_collection.\
                                           acquisitions[0].path_template)
        
        if self._data_collection.acquisitions[0].acquisition_parameters.\
                centred_position.snapshot_image:
            image = self._data_collection.acquisitions[0].\
                acquisition_parameters.centred_position.snapshot_image
            image = image.scale(427, 320)
            self.position_widget.svideo.setPixmap(QPixmap(image))

        self.toggle_permitted_range(self._char_params.use_permitted_rotation)
        self.enable_opt_parameters_widget(self._char_params.determine_rad_params)
        self.enable_maximum_res_ledit(self._char_params.use_aimed_resolution)
        self.enable_aimed_mult_ledit(self._char_params.use_aimed_multiplicity)
        
        item = self.char_type_widget.charact_type_tbox.\
            item(self._char_params.experiment_type)
        
        self.char_type_widget.charact_type_tbox.setCurrentItem(item)
        self.char_type_widget.toggle_time_dose()
        crystal = char.reference_image_collection.crystal
        self.acq_widget.set_energies(crystal.energy_scan_result)
