"""
Menu Abstract Class
"""

import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from pyqtspinner.spinner import WaitingSpinner


class MyMenu(QtWidgets.QWidget):
    """
    Second Menu:
    - Present Statistics
    - Choosing Weights
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(MyMenu, self).__init__(*args, **kwargs)

        self.parent = parent

        self.resize(width, height)

        self.main_layout = QtWidgets.QGridLayout()

        self.threadpool = QtCore.QThreadPool()
        self.wait = WaitingSpinner(self, True, True, QtCore.Qt.ApplicationModal, roundness=70.0, opacity=100.0,
                                   fade=70.0, radius=10.0, lines=12,
                                   line_length=10.0, line_width=5.0,
                                   speed=1.0, color=(0, 0, 0))

        self.setLayout(self.main_layout)

    def paintEvent(self, event):
        o = Qt.QStyleOption()
        o.initFrom(self)
        p = Qt.QPainter(self)
        self.style().drawPrimitive(Qt.QStyle.PE_Widget, o, p, self)

    def start_waiting(self):
        """
        """
        self.wait = WaitingSpinner(self, True, True, QtCore.Qt.ApplicationModal, roundness=70.0, opacity=100.0,
                                   fade=70.0, radius=10.0, lines=12,
                                   line_length=10.0, line_width=5.0,
                                   speed=1.0, color=(0, 0, 0))
        self.parent.btn_next.setEnabled(False)
        self.parent.btn_back.setEnabled(False)
        self.wait.start()

    def stop_waiting(self):
        """
        """
        self.parent.btn_next.setEnabled(True)
        self.parent.btn_back.setEnabled(True)
        self.wait.stop()

    def stop_waiting_next(self):
        """
        """
        self.stop_waiting()

        if self.parent.front_wid == 1:
            self.parent.wids[self.parent.front_wid + 1].set_maximum_spinbox()

        self.parent.next_wid_logic()

    def error_no_music(self, value):
        """
        Receive signal if no music to create statistics
        """
        msg = QtWidgets.QMessageBox()
        msg.setStyleSheet("""background: #b4b4b4;""")
        msg.setContentsMargins(5, 5, 5, 5)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("No Music! Go Back and select some!")
        msg.setWindowTitle('No Music Warning')
        msg.exec_()

    def stop_waiting_final(self):
        self.stop_waiting()

        msg = QtWidgets.QMessageBox()
        msg.setStyleSheet("""background: #b4b4b4;""")
        msg.setContentsMargins(5, 5, 5, 5)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Generation of Sequences Finished!!!")
        msg.setWindowTitle('Creator Finished')
        msg.exec_()

    def next(self):
        """
        To Override
        """
        pass

    def back(self):
        """
        To Override
        """
        self.parent.last_wid_logic()
