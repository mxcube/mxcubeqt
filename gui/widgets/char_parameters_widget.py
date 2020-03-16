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

from gui.utils import QtImport
from gui.utils.widget_utils import DataModelInputBinder
from gui.widgets.reference_image_widget import ReferenceImageWidget
from gui.widgets.char_type_widget import CharTypeWidget
from gui.widgets.optimisation_parameters_widget_layout import (
    OptimisationParametersWidgetLayout,
)

from HardwareRepository.HardwareObjects import (
    queue_model_objects,
    queue_model_enumerables,
)


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CharParametersWidget(QtImport.QWidget):
    def __init__(self, parent=None, name="char_parameter_widget"):

        QtImport.QWidget.__init__(self, parent)

        if name is not None:
            self.setObjectName(name)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self._char = None
        self._char_params = queue_model_objects.CharacterisationParameters()
        self._char_params_mib = DataModelInputBinder(self._char_params)
        self._tree_view_item = None
        self.previous_energy = None

        self.add_dc_cb = None

        # Graphic elements ----------------------------------------------------
        main_widget = QtImport.QWidget(self)
        rone_widget = QtImport.QWidget(main_widget)
        self.reference_img_widget = ReferenceImageWidget(rone_widget)
        self.acq_widget = self.reference_img_widget.acq_widget
        self.path_widget = self.reference_img_widget.path_widget
        self.position_widget = QtImport.load_ui_file("snapshot_widget_layout.ui")
        self.position_widget.setMinimumSize(450, 340)

        rtwo_widget = QtImport.QWidget(main_widget)
        self.char_type_widget = CharTypeWidget(rtwo_widget)
        self.routine_dc_widget = self.char_type_widget.routine_dc_page
        self.sad_widget = self.char_type_widget.sad_page
        self.rad_dmg_char_widget = self.char_type_widget.rad_damage_page
        self.opt_parameters_widget = OptimisationParametersWidgetLayout(self)

        rtree_widget = QtImport.QWidget(main_widget)
        self.rad_dmg_widget = QtImport.load_ui_file(
            "radiation_damage_model_widget_layout.ui"
        )
        self.vertical_dimension_widget = QtImport.load_ui_file(
            "vertical_crystal_dimension_widget_layout.ui"
        )

        # Layout --------------------------------------------------------------
        rone_widget_layout = QtImport.QHBoxLayout(rone_widget)
        rone_widget_layout.addWidget(self.reference_img_widget)
        rone_widget_layout.addWidget(self.position_widget)
        # rone_widget_layout.addStretch(0)
        rone_widget_layout.setSpacing(2)
        rone_widget_layout.setContentsMargins(0, 0, 0, 0)

        rtwo_widget_layout = QtImport.QHBoxLayout(rtwo_widget)
        rtwo_widget_layout.addWidget(self.char_type_widget)
        rtwo_widget_layout.addWidget(self.opt_parameters_widget)
        rtwo_widget_layout.addStretch(0)
        rtwo_widget_layout.setSpacing(2)
        rtwo_widget_layout.setContentsMargins(0, 0, 0, 0)

        rtree_widget_layout = QtImport.QHBoxLayout(rtree_widget)
        rtree_widget_layout.addWidget(self.rad_dmg_widget)
        rtree_widget_layout.addWidget(self.vertical_dimension_widget)
        rtree_widget_layout.addStretch(10)
        rtree_widget_layout.setSpacing(2)
        rtree_widget_layout.setContentsMargins(0, 0, 0, 0)

        _main_widget_vlayout = QtImport.QVBoxLayout(main_widget)
        _main_widget_vlayout.addWidget(rone_widget)
        _main_widget_vlayout.addWidget(rtwo_widget)
        _main_widget_vlayout.addWidget(rtree_widget)
        _main_widget_vlayout.addStretch(10)
        _main_widget_vlayout.setSpacing(2)
        _main_widget_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_hlayout = QtImport.QHBoxLayout(self)
        _main_hlayout.addWidget(main_widget)
        _main_hlayout.setSpacing(0)
        _main_hlayout.addStretch(0)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies -------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.toggle_permitted_range(
            self.opt_parameters_widget.opt_param_widget.permitted_range_cbx.isChecked()
        )

        self.opt_parameters_widget.opt_param_widget.permitted_range_cbx.toggled.connect(
            self.toggle_permitted_range
        )

        # Other ---------------------------------------------------------------
        self._char_params_mib.bind_value_update(
            "min_dose",
            self.routine_dc_widget.dose_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "min_time",
            self.routine_dc_widget.time_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "use_min_dose", self.routine_dc_widget.min_dose_radio, bool, None
        )

        self._char_params_mib.bind_value_update(
            "use_min_time", self.routine_dc_widget.min_time_radio, bool, None
        )

        self._char_params_mib.bind_value_update(
            "account_rad_damage",
            self.routine_dc_widget.radiation_damage_cbx,
            bool,
            None,
        )

        self._char_params_mib.bind_value_update(
            "auto_res", self.sad_widget.automatic_resolution_radio, bool, None
        )

        self._char_params_mib.bind_value_update(
            "sad_res",
            self.sad_widget.sad_resolution_ledit,
            float,
            QtImport.QDoubleValidator(0.5, 20, 3, self),
        )

        self._char_params_mib.bind_value_update(
            "opt_sad", self.sad_widget.optimised_sad_cbx, bool, None
        )

        self._char_params_mib.bind_value_update(
            "determine_rad_params", self.rad_dmg_char_widget.rad_damage_cbx, bool, None
        )

        self._char_params_mib.bind_value_update(
            "burn_osc_start",
            self.rad_dmg_char_widget.burn_osc_start_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "burn_osc_interval",
            self.rad_dmg_char_widget.burn_osc_interval_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "use_aimed_resolution",
            self.opt_parameters_widget.opt_param_widget.maximum_res_cbx,
            bool,
            None,
        )

        self._char_params_mib.bind_value_update(
            "use_aimed_multiplicity",
            self.opt_parameters_widget.opt_param_widget.aimed_mult_cbx,
            bool,
            None,
        )

        self._char_params_mib.bind_value_update(
            "aimed_resolution",
            self.opt_parameters_widget.opt_param_widget.maximum_res_ledit,
            float,
            QtImport.QDoubleValidator(0.01, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "aimed_multiplicity",
            self.opt_parameters_widget.opt_param_widget.aimed_mult_ledit,
            float,
            QtImport.QDoubleValidator(0.01, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "aimed_i_sigma",
            self.opt_parameters_widget.opt_param_widget.i_over_sigma_ledit,
            float,
            QtImport.QDoubleValidator(0.01, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "aimed_completness",
            self.opt_parameters_widget.opt_param_widget.aimed_comp_ledit,
            float,
            QtImport.QDoubleValidator(0.01, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "strategy_complexity",
            self.opt_parameters_widget.opt_param_widget.start_comp_cbox,
            int,
            None,
        )

        self._char_params_mib.bind_value_update(
            "use_permitted_rotation",
            self.opt_parameters_widget.opt_param_widget.permitted_range_cbx,
            bool,
            None,
        )

        self._char_params_mib.bind_value_update(
            "permitted_phi_start",
            self.opt_parameters_widget.opt_param_widget.phi_start_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "permitted_phi_end",
            self.opt_parameters_widget.opt_param_widget.phi_end_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "low_res_pass_strat",
            self.opt_parameters_widget.opt_param_widget.low_res_pass_cbx,
            bool,
            None,
        )

        self._char_params_mib.bind_value_update(
            "rad_suscept",
            self.rad_dmg_widget.sensetivity_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "beta",
            self.rad_dmg_widget.beta_over_gray_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "gamma",
            self.rad_dmg_widget.gamma_over_gray_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "max_crystal_vdim",
            self.vertical_dimension_widget.max_vdim_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "min_crystal_vdim",
            self.vertical_dimension_widget.min_vdim_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "min_crystal_vphi",
            self.vertical_dimension_widget.min_vphi_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        self._char_params_mib.bind_value_update(
            "max_crystal_vphi",
            self.vertical_dimension_widget.max_vphi_ledit,
            float,
            QtImport.QDoubleValidator(0.0, 1000, 2, self),
        )

        # self._char_params_mib.bind_value_update('space_group',
        #                                        self.vertical_dimension_widget.space_group_ledit,
        #                                        str,
        #                                        None)

        self.vertical_dimension_widget.space_group_ledit.addItems(
            queue_model_enumerables.XTAL_SPACEGROUPS
        )

        self.char_type_widget.charact_type_tbox.currentChanged.connect(
            self.update_char_type
        )
        self.rad_dmg_char_widget.rad_damage_cbx.toggled.connect(
            self.enable_opt_parameters_widget
        )
        self.opt_parameters_widget.opt_param_widget.maximum_res_cbx.toggled.connect(
            self.enable_maximum_res_ledit
        )
        self.opt_parameters_widget.opt_param_widget.aimed_mult_cbx.toggled.connect(
            self.enable_aimed_mult_ledit
        )
        self.path_widget.data_path_layout.prefix_ledit.textChanged.connect(
            self._prefix_ledit_change
        )
        self.path_widget.data_path_layout.run_number_ledit.textChanged.connect(
            self._run_number_ledit_change
        )
        self.vertical_dimension_widget.space_group_ledit.activated.connect(
            self._space_group_change
        )

    def _space_group_change(self, index):
        """
        Descript. :
        """
        self._char_params.space_group = queue_model_enumerables.XTAL_SPACEGROUPS[index]

    def _set_space_group(self, space_group):
        """
        Descript. :
        """
        index = 0

        if space_group in queue_model_enumerables.XTAL_SPACEGROUPS:
            index = queue_model_enumerables.XTAL_SPACEGROUPS.index(space_group)

        self._space_group_change(index)
        self.vertical_dimension_widget.space_group_ledit.setCurrentIndex(index)

    def _prefix_ledit_change(self, new_value):
        """
        Descript. :
        """
        prefix = self._data_collection.acquisitions[0].path_template.get_prefix()
        self._char.set_name(prefix)
        self._tree_view_item.setText(0, self._char.get_name())

    def _run_number_ledit_change(self, new_value):
        """
        Descript. :
        """
        if str(new_value).isdigit():
            self._char.set_number(int(new_value))
            self._tree_view_item.setText(0, self._char.get_name())

    def enable_aimed_mult_ledit(self, state):
        """
        Descript. :
        """
        self.opt_parameters_widget.opt_param_widget.aimed_mult_ledit.setEnabled(state)

    def enable_maximum_res_ledit(self, state):
        """
        Descript. :
        """
        self.opt_parameters_widget.opt_param_widget.maximum_res_ledit.setEnabled(state)

    def update_char_type(self, index):
        """
        Descript. :
        """
        self._char_params.experiment_type = index

    def toggle_permitted_range(self, status):
        """
        Descript. :
        """
        self.opt_parameters_widget.opt_param_widget.phi_start_ledit.setEnabled(status)
        self.opt_parameters_widget.opt_param_widget.phi_end_ledit.setEnabled(status)

    def enable_opt_parameters_widget(self, state):
        """
        Descript. :
        """
        if not self._char.is_executed():
            self.opt_parameters_widget.setEnabled(not state)
        else:
            self.opt_parameters_widget.setEnabled(False)

    def set_enabled(self, state):
        """
        Descript. :
        """
        self.char_type_widget.setEnabled(state)
        self.routine_dc_widget.setEnabled(state)
        self.sad_widget.setEnabled(state)
        self.rad_dmg_char_widget.setEnabled(state)
        self.reference_img_widget.setEnabled(state)
        self.acq_widget.setEnabled(state)
        self.path_widget.setEnabled(state)
        self.opt_parameters_widget.setEnabled(state)
        self.rad_dmg_widget.setEnabled(state)
        self.vertical_dimension_widget.setEnabled(state)

    def populate_parameter_widget(self, tree_view_item):
        """
        Descript. :
        """
        self._tree_view_item = tree_view_item
        self._char = tree_view_item.get_model()
        self._data_collection = self._char.reference_image_collection
        self._char_params = self._char.characterisation_parameters
        self._char_params_mib.set_model(self._char.characterisation_parameters)
        self._set_space_group(self._char_params.space_group)

        self.acq_widget.update_data_model(
            self._char.reference_image_collection.acquisitions[
                0
            ].acquisition_parameters,
            self._char.reference_image_collection.acquisitions[0].path_template,
        )

        self.path_widget.update_data_model(
            self._char.reference_image_collection.acquisitions[0].path_template
        )

        if self._data_collection.acquisitions[
            0
        ].acquisition_parameters.centred_position.snapshot_image:
            image = self._data_collection.acquisitions[
                0
            ].acquisition_parameters.centred_position.snapshot_image
            ration = image.height() / float(image.width())
            image = image.scaled(
                400,
                400 * ration,
                QtImport.Qt.KeepAspectRatio,
                QtImport.Qt.SmoothTransformation,
            )
            self.position_widget.svideo.setPixmap(QtImport.QPixmap(image))

        self.toggle_permitted_range(self._char_params.use_permitted_rotation)
        self.enable_opt_parameters_widget(self._char_params.determine_rad_params)
        self.enable_maximum_res_ledit(self._char_params.use_aimed_resolution)
        self.enable_aimed_mult_ledit(self._char_params.use_aimed_multiplicity)

        item = self.char_type_widget.charact_type_tbox.widget(
            self._char_params.experiment_type
        )
        if item:
            self.char_type_widget.charact_type_tbox.setCurrentWidget(item)
        self.char_type_widget.toggle_time_dose()
        crystal = self._char.reference_image_collection.crystal
        self.acq_widget.set_energies(crystal.energy_scan_result)
