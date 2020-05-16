"""
Menu Abstract Class
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets

from interface.waiting_spinner import QtWaitingSpinner


class MyMenu(QtWidgets.QWidget):
    """
    Second Menu:
    - Present Statistics
    - Choosing Weights
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(MyMenu, self).__init__(*args, **kwargs)

        self.resize(width, height)

        self.main_layout = QtWidgets.QGridLayout()

        self.wait = QtWaitingSpinner()
        self.main_layout.addWidget(self.wait)
        # self.wait.start()

        self.setLayout(self.main_layout)

    def paintEvent(self, event):
        o = Qt.QStyleOption()
        o.initFrom(self)
        p = Qt.QPainter(self)
        self.style().drawPrimitive(Qt.QStyle.PE_Widget, o, p, self)
    
    def next(self):
        """
        To Override
        """
        pass

    def back(self):
        """
        To Override
        """
        pass
