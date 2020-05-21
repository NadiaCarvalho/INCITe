"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets

from interface.menus.menu import MyMenu


class ThirdMenu(MyMenu):
    """
    Third Menu:
    - Choosing
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(ThirdMenu, self).__init__(width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: light gray;""")

        self.number_sequences = 15
        self.number_lines = 1

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
        widget = QtWidgets.QGroupBox("Oracle and Generator")
        widget.setStyleSheet("""color: blue; font: bold 20px;""")

        layout = QtWidgets.QFormLayout()

        layout.setContentsMargins(5, 45, 5, 5)
        layout.setSpacing(50)

        label_2 = QtWidgets.QLabel("Number of lines to generate:")
        label_2.setStyleSheet("""color: black; font: bold 16px;""")

        spin_box_2 = QtWidgets.QSpinBox()
        spin_box_2.setValue(self.number_lines)
        spin_box_2.valueChanged.connect(self.change_number_lines)

        layout.addRow(label_2, spin_box_2)

        button_box = QtWidgets.QPushButton("Generate Oracle")
        button_box.setStyleSheet("""color: black; font: bold 16px;""")
        button_box.clicked.connect(self.create_oracle)
        layout.addWidget(button_box)

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
        spin_box_1.setValue(self.number_sequences)
        spin_box_1.valueChanged.connect(self.change_number_seq)

        layout.addRow(label_1, spin_box_1)

        button_box = QtWidgets.QPushButton("Generate Oracle")
        button_box.setStyleSheet("""color: black; font: bold 16px;""")
        button_box.clicked.connect(self.generate_sequences_oracle)
        layout.addWidget(button_box)

        widget.setLayout(layout)
        return widget

    def set_maximum_spinbox(self):
        """
        Set Maximum Value of line spinbox
        """
        possible_parts = [len(list(_tuple[0].get_part_events()))
                          for music, _tuple in
                          self.parentWidget().parentWidget().application.music.items()]
        self.children()[2].children()[2].setMaximum(max(possible_parts))

    def create_oracle(self):
        """
        Call Generator
        """
        self.parentWidget().parentWidget().application.generate_oracle(
            self, self.number_lines)

    def generate_sequences_oracle(self):
        """
        Call Generator
        """
        self.parentWidget().parentWidget().application.generate_sequences(
            self.number_lines, self.number_sequences)

    def change_number_seq(self, value):
        """
        Handle for spinbox sequence number
        """
        self.number_sequences = value

    def change_number_lines(self, value):
        """
        Handle for spinbox line number
        """
        self.number_lines = value

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