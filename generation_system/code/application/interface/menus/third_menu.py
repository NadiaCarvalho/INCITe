"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from application.interface.components.qline import QHLine
from application.interface.components.qworker import Worker
from application.interface.menus.menu import MyMenu


class ThirdMenu(MyMenu):
    """
    Third Menu:
    - Choosing
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(ThirdMenu, self).__init__(width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: #b4b4b4;""")

        self.number_sequences = 15
        self.line = True
        self.part = 1

        self.container = self.create_container_oracle(parent)

        bottom_spacer = QtWidgets.QWidget()
        bottom_spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(35)

        self.main_layout.addWidget(self.container, 0, 0, 14, 2)
        self.main_layout.addWidget(bottom_spacer, 15, 0, 1, 2)

    def create_container_oracle(self, parent):
        """
        Principal Container
        """
        widget = QtWidgets.QGroupBox("Oracle Creation:")
        widget.setStyleSheet("""color: blue; font: bold 20px;""")

        layout = QtWidgets.QFormLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        layout.setContentsMargins(5, 45, 5, 5)
        layout.setSpacing(50)

        radio_button_1 = QtWidgets.QRadioButton("One Line Oracle")
        radio_button_1.setChecked(True)
        radio_button_1.setStyleSheet("""color: black; font: bold 16px;""")
        radio_button_1.toggled.connect(self.radio_clicked)

        radio_button_2 = QtWidgets.QRadioButton("Multiple Line Oracle")
        radio_button_2.setChecked(False)
        radio_button_2.setStyleSheet("""color: black; font: bold 16px;""")
        radio_button_2.toggled.connect(self.radio_clicked)

        layout.addRow(radio_button_1, radio_button_2)

        layout.addWidget(QHLine())

        label_1 = QtWidgets.QLabel("Part from Which to Generate:")
        label_1.setStyleSheet("""color: black; font: bold 16px;""")

        combo_box_1 = QtWidgets.QComboBox()
        combo_box_1.currentIndexChanged.connect(self.change_line)
        layout.addRow(label_1, combo_box_1)

        button_box = QtWidgets.QPushButton("Generate Oracle")
        button_box.setStyleSheet("""color: black; font: bold 16px;""")
        button_box.clicked.connect(self.create_oracle)
        layout.addWidget(button_box)

        layout.addWidget(QHLine())

        widget.setLayout(layout)
        return widget

    def sequencer_container(self):
        """
        Create Sequence Container
        """
        widget = QtWidgets.QGroupBox("Sequence Generator")
        widget.setStyleSheet("""color: blue; font: bold 20px;""")

        layout = QtWidgets.QFormLayout()

        layout.setContentsMargins(5, 45, 5, 5)
        layout.setSpacing(50)

        label_1 = QtWidgets.QLabel("Number of sequences to generate:")
        label_1.setStyleSheet("""color: black; font: bold 16px;""")

        spin_box_1 = QtWidgets.QSpinBox()
        spin_box_1.setMinimum(1)
        spin_box_1.setValue(self.number_sequences)
        spin_box_1.valueChanged.connect(self.change_number_seq)

        layout.addRow(label_1, spin_box_1)

        button_box = QtWidgets.QPushButton("Generate Sequences")
        button_box.setStyleSheet("""color: black; font: bold 16px;""")
        button_box.clicked.connect(self.generate_sequences_oracle)
        layout.addWidget(button_box)

        widget.setLayout(layout)
        return widget

    def radio_clicked(self):
        """
        One/Multiple Button
        """
        radio_button = self.sender()
        if radio_button.isChecked() and 'One' in radio_button.text():
            self.line = True
            self.children()[2].children()[5].setEnabled(True)
        else:
            self.line = False
            self.children()[2].children()[5].setEnabled(False)

    def set_maximum_spinbox(self):
        """
        Set Maximum Value of line spinbox
        """
        if self.parentWidget().parentWidget().application.principal_music is not None:
            self.possible_parts = list(self.parentWidget().parentWidget().application.principal_music[0].get_part_events().keys())
            self.possible_parts = [str(pp) for pp in self.possible_parts]

            if len(self.possible_parts) == 1:
                self.children()[2].children()[5].setEnabled(False)
            else:
                self.children()[2].children()[5].setEnabled(True)

            self.children()[2].children()[5].addItems(self.possible_parts)


    def create_oracle(self):
        """
        Call Oracle Generator
        """
        application = self.parentWidget().parentWidget().application
        worker = Worker(
            application.generate_oracle, self, self.line, self.part)
        worker.signals.finished.connect(self.stop_waiting)
        self.threadpool.start(worker)
        self.start_waiting()

    def generate_sequences_oracle(self):
        """
        Call Sequence Generator
        """
        application = self.parentWidget().parentWidget().application
        worker = Worker(
            application.generate_sequences, self.line, self.number_sequences)
        worker.signals.finished.connect(self.stop_waiting_final)
        self.threadpool.start(worker)
        self.start_waiting()

    def change_line(self, value):
        """
        Handle for spinbox sequence number
        """
        if len(self.possible_parts) > 0:
            self.part = self.possible_parts[value]

    def change_number_seq(self, value):
        """
        Handle for spinbox sequence number
        """
        self.number_sequences = value

    def handler_create_sequence(self, int):
        """
        Handle the creation of the group box for
        Sequence Handling
        """
        new_container = self.sequencer_container()
        self.main_layout.addWidget(new_container, 6, 0, 10, 2)

        bottom_spacer = QtWidgets.QWidget()
        bottom_spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.main_layout.addWidget(bottom_spacer, 16, 0, 1, 2)
