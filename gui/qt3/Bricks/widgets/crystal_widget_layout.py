# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/crystal_widget_layout.ui'
#
# Created: Fri Jun 21 15:28:23 2013
#      by: The PyQt User Interface Compiler (pyuic) 3.18.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class CrystalWidgetLayout(QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName("CrystalWidgetLayout")

        CrystalWidgetLayoutLayout = QHBoxLayout(self, 0, 6, "CrystalWidgetLayoutLayout")

        self.gbox = QGroupBox(self, "gbox")
        self.gbox.setColumnLayout(0, Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = QVBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(Qt.AlignTop)

        rone_layout = QHBoxLayout(None, 0, 6, "rone_layout")

        rone_content_layout = QHBoxLayout(None, 0, 6, "rone_content_layout")

        rone_label_layout = QVBoxLayout(None, 0, 6, "rone_label_layout")

        self.protein_acronym_label = QLabel(self.gbox, "protein_acronym_label")
        rone_label_layout.addWidget(self.protein_acronym_label)

        self.space_group_label = QLabel(self.gbox, "space_group_label")
        rone_label_layout.addWidget(self.space_group_label)

        self.monomers_asym_unit_label = QLabel(self.gbox, "monomers_asym_unit_label")
        rone_label_layout.addWidget(self.monomers_asym_unit_label)

        self.amino_acid_residiues_label = QLabel(
            self.gbox, "amino_acid_residiues_label"
        )
        rone_label_layout.addWidget(self.amino_acid_residiues_label)

        self.dna_nucleotides_label = QLabel(self.gbox, "dna_nucleotides_label")
        rone_label_layout.addWidget(self.dna_nucleotides_label)

        self.rna_nucleotides_label = QLabel(self.gbox, "rna_nucleotides_label")
        rone_label_layout.addWidget(self.rna_nucleotides_label)
        rone_content_layout.addLayout(rone_label_layout)

        rone_value_layout = QVBoxLayout(None, 0, 6, "rone_value_layout")

        self.protein_acronym_value_label = QLabel(
            self.gbox, "protein_acronym_value_label"
        )
        rone_value_layout.addWidget(self.protein_acronym_value_label)

        self.space_group_value_label = QLabel(self.gbox, "space_group_value_label")
        rone_value_layout.addWidget(self.space_group_value_label)

        self.monomers_asym_unit_value_label = QLabel(
            self.gbox, "monomers_asym_unit_value_label"
        )
        rone_value_layout.addWidget(self.monomers_asym_unit_value_label)

        self.amino_acid_residiues_value_label = QLabel(
            self.gbox, "amino_acid_residiues_value_label"
        )
        rone_value_layout.addWidget(self.amino_acid_residiues_value_label)

        self.dna_nucleotides_value_label = QLabel(
            self.gbox, "dna_nucleotides_value_label"
        )
        rone_value_layout.addWidget(self.dna_nucleotides_value_label)

        self.rna_nucleotides_value_label = QLabel(
            self.gbox, "rna_nucleotides_value_label"
        )
        rone_value_layout.addWidget(self.rna_nucleotides_value_label)
        rone_content_layout.addLayout(rone_value_layout)
        rone_layout.addLayout(rone_content_layout)
        hspacer = QSpacerItem(76, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        rone_layout.addItem(hspacer)
        gboxLayout.addLayout(rone_layout)

        rtwo_layout = QHBoxLayout(None, 0, 6, "rtwo_layout")

        rtwo_content_layout = QVBoxLayout(None, 0, 2, "rtwo_content_layout")

        unit_cell_heading_layout = QHBoxLayout(None, 0, 6, "unit_cell_heading_layout")

        self.unit_cell_heading = QLabel(self.gbox, "unit_cell_heading")
        unit_cell_heading_layout.addWidget(self.unit_cell_heading)
        unit_cell_spacer = QSpacerItem(
            1, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        unit_cell_heading_layout.addItem(unit_cell_spacer)
        rtwo_content_layout.addLayout(unit_cell_heading_layout)

        rtwo_value_layout = QHBoxLayout(None, 0, 6, "rtwo_value_layout")

        a_layout = QHBoxLayout(None, 0, 6, "a_layout")

        self.a_label = QLabel(self.gbox, "a_label")
        a_layout.addWidget(self.a_label)

        self.a_value_label = QLabel(self.gbox, "a_value_label")
        self.a_value_label.setMinimumSize(QSize(35, 0))
        self.a_value_label.setMaximumSize(QSize(25, 32767))
        a_layout.addWidget(self.a_value_label)
        rtwo_value_layout.addLayout(a_layout)

        b_layout = QHBoxLayout(None, 0, 6, "b_layout")

        self.b_label = QLabel(self.gbox, "b_label")
        b_layout.addWidget(self.b_label)

        self.b_value_label = QLabel(self.gbox, "b_value_label")
        self.b_value_label.setMinimumSize(QSize(35, 0))
        self.b_value_label.setMaximumSize(QSize(35, 32767))
        b_layout.addWidget(self.b_value_label)
        rtwo_value_layout.addLayout(b_layout)

        c_layout = QHBoxLayout(None, 0, 6, "c_layout")

        self.c_label = QLabel(self.gbox, "c_label")
        self.c_label.setMinimumSize(QSize(0, 0))
        self.c_label.setMaximumSize(QSize(32767, 32767))
        c_layout.addWidget(self.c_label)

        self.c_value_label = QLabel(self.gbox, "c_value_label")
        self.c_value_label.setMinimumSize(QSize(35, 0))
        self.c_value_label.setMaximumSize(QSize(35, 32767))
        c_layout.addWidget(self.c_value_label)
        rtwo_value_layout.addLayout(c_layout)

        alpha_layout = QHBoxLayout(None, 0, 6, "alpha_layout")

        self.alpha_label = QLabel(self.gbox, "alpha_label")
        alpha_layout.addWidget(self.alpha_label)

        self.alpha_value_label = QLabel(self.gbox, "alpha_value_label")
        self.alpha_value_label.setMinimumSize(QSize(35, 0))
        self.alpha_value_label.setMaximumSize(QSize(35, 32767))
        alpha_layout.addWidget(self.alpha_value_label)
        rtwo_value_layout.addLayout(alpha_layout)

        beta_layout = QHBoxLayout(None, 0, 6, "beta_layout")

        self.beta_label = QLabel(self.gbox, "beta_label")
        beta_layout.addWidget(self.beta_label)

        self.beta_value_label = QLabel(self.gbox, "beta_value_label")
        self.beta_value_label.setMinimumSize(QSize(35, 0))
        self.beta_value_label.setMaximumSize(QSize(35, 32767))
        beta_layout.addWidget(self.beta_value_label)
        rtwo_value_layout.addLayout(beta_layout)

        gamma_layout = QHBoxLayout(None, 0, 6, "gamma_layout")

        self.gamma_label = QLabel(self.gbox, "gamma_label")
        gamma_layout.addWidget(self.gamma_label)

        self.gamma_value_label = QLabel(self.gbox, "gamma_value_label")
        self.gamma_value_label.setMinimumSize(QSize(35, 0))
        self.gamma_value_label.setMaximumSize(QSize(35, 32767))
        gamma_layout.addWidget(self.gamma_value_label)
        rtwo_value_layout.addLayout(gamma_layout)
        rtwo_content_layout.addLayout(rtwo_value_layout)
        rtwo_layout.addLayout(rtwo_content_layout)
        unit_cell_layout = QSpacerItem(
            16, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        rtwo_layout.addItem(unit_cell_layout)
        gboxLayout.addLayout(rtwo_layout)
        CrystalWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(QSize(409, 229).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("CrystalWidget"))
        self.gbox.setTitle(self.__tr("Crystal:"))
        self.protein_acronym_label.setText(self.__tr("Protein acronym"))
        self.space_group_label.setText(self.__tr("Space group:"))
        self.monomers_asym_unit_label.setText(self.__tr("Monomers in assymetric unit:"))
        self.amino_acid_residiues_label.setText(
            self.__tr("Amino acid residiues per monomer:")
        )
        self.dna_nucleotides_label.setText(self.__tr("DNA nucleotides per monomer:"))
        self.rna_nucleotides_label.setText(self.__tr("RNA nucleotides per monomer:"))
        self.protein_acronym_value_label.setText(QString.null)
        self.space_group_value_label.setText(QString.null)
        self.monomers_asym_unit_value_label.setText(QString.null)
        self.amino_acid_residiues_value_label.setText(QString.null)
        self.dna_nucleotides_value_label.setText(QString.null)
        self.rna_nucleotides_value_label.setText(QString.null)
        self.unit_cell_heading.setText(self.__tr("Unit cell:"))
        self.a_label.setText(self.__tr("a:"))
        self.b_label.setText(self.__tr("b:"))
        self.c_label.setText(self.__tr("c:"))
        self.alpha_label.setText(self.__trUtf8("\xce\xb1\x3a"))
        self.beta_label.setText(self.__trUtf8("\xce\xb2\x3a"))
        self.gamma_label.setText(self.__trUtf8("\xce\xb3\x3a"))

    def __tr(self, s, c=None):
        return qApp.translate("CrystalWidgetLayout", s, c)

    def __trUtf8(self, s, c=None):
        return qApp.translate("CrystalWidgetLayout", s, c, QApplication.UnicodeUTF8)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a, SIGNAL("lastWindowClosed()"), a, SLOT("quit()"))
    w = CrystalWidgetLayout()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
