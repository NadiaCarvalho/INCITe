import sys

from PyQt5.QtCore import Qt
from PyQt5 import Qt, QtWidgets, QtGui


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("My Awesome App")
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.resize(400,800)

        # Central Widget
        self.central_wid = QtWidgets.QWidget()
        self.layout_for_wids =  QtWidgets.QStackedLayout()

        self.addToolBar(self.init_toolbar())

        # LAYOUT CONTAINER FOR WIDGETS
        self.wids = [self.first_menu(), self.second_menu(), self.third_menu()]
        for wind in self.wids:
            self.layout_for_wids.addWidget(wind)

        self.front_wid = 0
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

    def first_menu(self):
        """
        Initiation of first Menu:
        - Choosing Database
        """
        wid = QtWidgets.QWidget()
        wid.setStyleSheet("""background: blue;""")
        wid.resize(self.width(), self.height())
        return wid

    def second_menu(self):
        """
        Initiation of second Menu:
        - Presentation of statistics 
        - Choosing Weights
        """
        wid = QtWidgets.QWidget()
        wid.setStyleSheet("""background: red;""")
        wid.resize(self.width(), self.height())
        return wid

    def third_menu(self):
        """
        Initiation of third Menu
        - Oracles constructed (maybe show?)
        - Choosing number of sequences to generate
        - Generate
        """
        wid = QtWidgets.QWidget()
        wid.setStyleSheet("""background: green;""")
        wid.resize(self.width(), self.height())
        return wid

    def next_wid(self):
        # LOGIC TO SWITCH NEXT
        if self.front_wid != len(self.wids)-1:
            self.wids[self.front_wid].hide()
            self.front_wid += 1
            self.wids[self.front_wid].show()
            self.switch_state_buttons()

    def last_wid(self):
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
            


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
