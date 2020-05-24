"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets, QtCore

from interface.menus.menu import MyMenu

class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)

class ThirdMenu(MyMenu):
    """
    Third Menu:
    - Choosing
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(ThirdMenu, self).__init__(width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: light gray;""")

        self.number_sequences = 15
        self.line = True
        self.part = 0

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

        line_splitter = QHLine()
        layout.addWidget(line_splitter)

        label_1 = QtWidgets.QLabel("Part from Which to Generate:")
        label_1.setStyleSheet("""color: black; font: bold 16px;""")

        spin_box_1 = QtWidgets.QSpinBox()
        spin_box_1.setValue(self.part)
        spin_box_1.valueChanged.connect(self.change_number_seq)

        layout.addRow(label_1, spin_box_1)

        button_box = QtWidgets.QPushButton("Generate Oracle")
        button_box.setStyleSheet("""color: black; font: bold 16px;""")
        button_box.clicked.connect(self.create_oracle)
        layout.addWidget(button_box)

        line_splitter = QHLine()
        layout.addWidget(line_splitter)

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
        else:
            self.line = False

    def set_maximum_spinbox(self):
        """
        Set Maximum Value of line spinbox
        """
        possible_parts = [len(list(_tuple[0].get_part_events()))
                          for music, _tuple in
                          self.parentWidget().parentWidget().application.music.items()]
        if max(possible_parts) == 1:
            self.children()[2].children()[2].setEnabled(False)
        else:
            self.children()[2].children()[3].setEnabled(True)

    def create_oracle(self):
        """
        Call Oracle Generator
        """
        self.parentWidget().parentWidget().application.generate_oracle(
            self, self.line)

    def generate_sequences_oracle(self):
        """
        Call Sequence Generator
        """
        self.parentWidget().parentWidget().application.generate_sequences(
            self.line, self.number_sequences)

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
