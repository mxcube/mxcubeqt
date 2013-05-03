from qt import *


class CreateMeshWidget(QWidget):
    def __init__(self, parent = None, name = None, fl = 0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("mesh_widget")

        # tool_box->method->group_box->position_history_widget->position_history_brick
        self.pos_hbrick = self.parent().parent().parent().parent()

        v_layout = QVBoxLayout(self, 15, 15, "v_layout")
        row_one_hlayout = QHBoxLayout(v_layout, 10, "row_one")
        col_one_vlayout = QVBoxLayout(row_one_hlayout, 5, "col_one")
        col_two_vlayout = QVBoxLayout(row_one_hlayout, 5, "col_two")
        row_two_hlayout = QHBoxLayout(v_layout, 10, "row_two")
        row_one_hlayout.addStretch()

        rows_label = QLabel("Rows:", self)
        cols_label = QLabel("Cols:", self)
        rows_ledit = QLineEdit(self)
        rows_ledit.setMaximumSize(QSize(50,25))
        cols_ledit = QLineEdit(self)
        cols_ledit.setMaximumSize(QSize(50,25))
        
        grab_button = QPushButton("Grab", self)
        show_button = QPushButton("Show", self)
        
        col_one_vlayout.addWidget(rows_label)
        col_one_vlayout.addWidget(cols_label)

        col_two_vlayout.addWidget(rows_ledit)
        col_two_vlayout.addWidget(cols_ledit)

        row_two_hlayout.addWidget(grab_button)
        row_two_hlayout.addWidget(show_button)

        v_layout.addStretch()


        

        
