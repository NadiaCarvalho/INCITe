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
    def __init__(self, width, height, *args, **kwargs):
        super(MyMenu, self).__init__(*args, **kwargs)

        self.resize(width, height)

        self.mainLayout = QtWidgets.QGridLayout()

        self.wait = QtWaitingSpinner()
        self.mainLayout.addWidget(self.wait)
        #self.wait.start()
        
        self.setLayout(self.mainLayout)

    def paintEvent(self, event):
        o = Qt.QStyleOption()
        o.initFrom(self)
        p = Qt.QPainter(self)
        self.style().drawPrimitive(Qt.QStyle.PE_Widget, o, p, self)