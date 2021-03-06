"""
Main Window for Interface
"""
import os
import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from application.interface.menus.first_menu import FirstMenu
from application.interface.menus.second_menu import SecondMenu
from application.interface.menus.third_menu import ThirdMenu

from application.logic import Application

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.sep.join(['.', 'data', 'images'])
        base_path = os.path.abspath(base_path)

    return os.path.join(base_path, relative_path)

class MainWindow(QtWidgets.QMainWindow):
    """
    Main Window of Application
    """

    def __init__(self, music, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("My Musical Suggester")

        self.setWindowIcon(QtGui.QIcon(resource_path("logo.ico")))

        self.application = Application(music)

        self.resize(500, 700)

        # Central Widget
        self.central_wid = QtWidgets.QWidget()
        self.layout_for_wids = QtWidgets.QStackedLayout()
        self.layout_for_wids.setContentsMargins(0, 0, 0, 4)
        self.layout_for_wids.setSpacing(15)

        f_m = FirstMenu(self.width(), self.height(), self)
        s_m = SecondMenu(self.width(), self.height(), self)
        t_m = ThirdMenu(self.width(), self.height(), self)
        self.wids = [f_m, s_m, t_m]
        self.front_wid = 0

        self.addToolBar(self.init_toolbar())

        # LAYOUT CONTAINER FOR WIDGETS
        for wind in self.wids:
            self.layout_for_wids.addWidget(wind)

        self.wids[self.front_wid].show()

        # ENTERING LAYOUT
        self.central_wid.setLayout(self.layout_for_wids)

        # CHOOSE YOUR CENTRAL WIDGET
        self.setCentralWidget(self.central_wid)

    def resizeEvent(self, event):
        """
        Override to make menus resize on resize of window
        """
        for wind in self.wids:
            wind.resize(self.width(), self.height())
        self.layout_for_wids.setContentsMargins(0, 0, 0, 4)
        self.layout_for_wids.setSpacing(15)

    def init_toolbar(self):
        """
        Create Toolbar
        - next/back buttons
        """
        toolbar = QtWidgets.QToolBar("My main toolbar")

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Back Window Button
        self.btn_back = QtWidgets.QAction("Back", self)
        self.btn_back.triggered.connect(self.last_wid)
        self.btn_back.setShortcut('Ctrl+Q')
        self.btn_back.setEnabled(False)
        self.btn_back.setToolTip('Go to last window')

        # Next Window Button
        self.btn_next = QtWidgets.QAction("Next", self)
        self.btn_next.triggered.connect(self.next_wid)
        self.btn_next.setShortcut('Ctrl+Q')
        self.btn_next.setToolTip('Go to next window')

        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # TOOLBAR BUTTONS
        toolbar.addWidget(left_spacer)
        toolbar.addAction(self.btn_back)
        toolbar.addAction(self.btn_next)
        toolbar.addWidget(right_spacer)
        return toolbar

    def next_wid(self):
        self.wids[self.front_wid].next()

    def next_wid_logic(self):
        # LOGIC TO SWITCH NEXT
        if self.front_wid != len(self.wids)-1:
            self.wids[self.front_wid].hide()
            self.front_wid += 1
            self.wids[self.front_wid].show()
            self.switch_state_buttons()

    def last_wid(self):
        self.wids[self.front_wid].back()

    def last_wid_logic(self):
        # LOGIC TO SWITCH BACK
        if self.front_wid > 0:
            self.wids[self.front_wid].hide()
            self.front_wid -= 1
            self.wids[self.front_wid].show()
            self.switch_state_buttons()

    def switch_state_buttons(self):
        """
        Switch selectable state of buttons
        """
        self.btn_next.setEnabled(True)
        self.btn_back.setEnabled(True)

        if self.front_wid == len(self.wids)-1:
            self.btn_next.setEnabled(False)
        if self.front_wid == 0:
            self.btn_back.setEnabled(False)
