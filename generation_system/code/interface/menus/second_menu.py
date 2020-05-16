"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets

from interface.menus.menu import MyMenu


class SecondMenu(MyMenu):
    """
    Second Menu:
    - Present Statistics
    - Choosing Weights
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(SecondMenu, self).__init__(
            width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: gray;""")

        self.top_group = self.create_settings(parent, width)
        self.top_group.layout().setContentsMargins(5, 5, 10, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(QtWidgets.QVBoxLayout(self.container))
        self.container.layout().setContentsMargins(5, 5, 5, 5)

        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(35)

        bottom_spacer = QtWidgets.QWidget()
        bottom_spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.main_layout.addWidget(self.top_group, 0, 0, 1, 2)
        self.main_layout.addWidget(self.container, 1, 0, 14, 2)
        self.main_layout.addWidget(bottom_spacer, 15, 0, 1, 2)

    def resizeEvent(self, event):
        """
        Override of resizeEvent for override path text
        """
        self.main_layout.setContentsMargins(5, 5, 5, 5)

    def create_settings(self, parent, width):
        """
        Create database settings Grouping
        - Start Viewpoint Statistics
        - Choose Automatic Statistics
        """
        database_group = QtWidgets.QWidget()
        database_group.setStyleSheet("margin-left: 10px; padding: 15px;")
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(3, 3, 3, 3)

        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 2)

        button = QtWidgets.QPushButton('View Statistics')
        button.clicked.connect(self.calculate_statistics)
        layout.addWidget(button, 0, 0, 1, 1)

        button = QtWidgets.QPushButton('Choose Automatic Viewpoints')
        # button.clicked.connect(self.database_path)
        layout.addWidget(button, 0, 1, 1, 1)

        database_group.setLayout(layout)
        return database_group

    def calculate_statistics(self):
        """
        Calculate satistics for music
        """
        self.parentWidget().parentWidget().application.calculate_statistics(self)

    def create_statistics_overview(self, statistics):
        """
        Receive signal for presenting statistics
        """
        if self.container.layout() is not None:
            for i in range(self.container.layout().count()):
                self.container.layout().itemAt(i).widget().close()
        
        # Initialize tab screen
        tabs = QtWidgets.QTabWidget()
        tab_parts = self.create_part_statistics(statistics['parts'], tabs)
        tab_vert = self.create_vert_statistics(statistics['vert'], tabs)

        # Add tabs
        tabs.addTab(tab_parts, "Part Events")
        tabs.addTab(tab_vert, "Vertical Events")

        # Add tabs to widget
        self.container.layout().addWidget(tabs)

    def create_part_statistics(self, statistics, tabs):
        """
        """
        part_widget = QtWidgets.QWidget()

        # Create first tab
        part_widget.setLayout(QtWidgets.QVBoxLayout(tabs))
        listWid = QtWidgets.QListWidget()
        part_widget.layout().addWidget(listWid)

        return part_widget

    def create_vert_statistics(self, statistics, tabs):
        """
        """
        vert_widget = QtWidgets.QWidget()

        # Create first tab
        vert_widget.setLayout(QtWidgets.QVBoxLayout(tabs))
        pushButton1 = QtWidgets.QPushButton("PyQt5 button")
        vert_widget.layout().addWidget(pushButton1)

        return vert_widget
