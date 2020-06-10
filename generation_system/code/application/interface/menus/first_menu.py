"""
Main Window for Interface
"""

import copy
import os
import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from application.interface.components.qworker import Worker
from application.interface.components.wrap_text import wrap_text
from application.interface.menus.menu import MyMenu


class OnOffWidget(QtWidgets.QWidget):
    def __init__(self, name):
        super(OnOffWidget, self).__init__()

        self.name = name  # Name of widget used

        self.lbl = QtWidgets.QLabel(self.name)  # The widget label
        self.btn_del = QtWidgets.QPushButton("Del")  # The DEL button
        self.btn_del.clicked.connect(self.on_delete)

        # A horizontal layout to encapsulate the above
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.lbl)   # Add the label to the layout
        self.hbox.addWidget(self.btn_del)    # Add the DEL button to the layout
        self.setLayout(self.hbox)

    def on_delete(self):
        group_box = self.parentWidget().parentWidget().parentWidget().parentWidget()
        menu = group_box.parentWidget()

        for filename in menu.files_to_parse:
            if self.name in filename:
                menu.files_to_parse.remove(filename)
                break
        if len([widget for widget in self.parentWidget().children() if isinstance(widget, OnOffWidget)]) == 1:
            group_box.children()[2].setVisible(False)
        self.parentWidget().layout().removeWidget(self)
        self.deleteLater()
        self = None


class FirstMenu(MyMenu):
    """
    First Menu:
    - Choosing Database
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(FirstMenu, self).__init__(width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: #b4b4b4;""")

        self.top_group = self.create_settings(parent, width)
        self.left_group_box = self.create_database_group(parent)
        self.right_group_box = self.create_add_your_own_group()

        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.main_layout.addWidget(self.top_group, 0, 0, 1, 2)
        self.main_layout.addWidget(self.left_group_box, 1, 0, 14, 1)
        self.main_layout.addWidget(self.right_group_box, 1, 1, 14, 1)

        self.files_to_parse = []

    def resizeEvent(self, event):
        """
        Override of resizeEvent for override path text
        """
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        text = self.top_group.children()[2].text()
        self.top_group.children()[2].setText(
            wrap_text(text, int(self.width()*30/420)))

    def create_settings(self, parent, width):
        """
        Create database settings Grouping
        - Choose and Show database path
        """
        database_group = QtWidgets.QWidget()
        database_group.setStyleSheet("margin-left: 10px; padding: 15px;")
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(3, 3, 3, 3)

        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 10)

        button = QtWidgets.QPushButton('Select Database Path')
        button.clicked.connect(self.database_path)
        layout.addWidget(button, 0, 0, 1, 1)

        self.label = QtWidgets.QLabel(
            wrap_text(parent.application.database_path, int(self.width()*30/420)))
        self.label.setStyleSheet(
            "margin-left: 10px; border-radius: 25px; color: blue;")
        layout.addWidget(self.label, 0, 1, 1, 2)

        database_group.setLayout(layout)
        return database_group

    def database_path(self):
        """
        File Dialog for selecting database path, called with button
        - Choose database path, using a file dialog
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", options=options)
        if directory:
            application = self.parentWidget().parentWidget().application
            application.database_path = directory
            self.label.setText(
                wrap_text(directory, int(self.width()*30/420)))

            self.create_toggables_database(
                directory, self.left_group_box.children()[2])

    def create_database_group(self, parent):
        """
        Creates a viewer and chooser for already existent database
        """
        database_group = QtWidgets.QGroupBox("Database")
        layout = QtWidgets.QVBoxLayout()

        check_box = QtWidgets.QCheckBox("Select All")
        check_box.setTristate(True)
        check_box.setChecked(False)
        check_box.stateChanged.connect(self.select_all)
        check_box.clicked.connect(self.click_pass_semi)

        layout.addWidget(check_box)

        scrollable_container = self.create_container_files()

        selectables = self.create_toggables_database(
            parent.application.database_path, scrollable_container)

        layout.addWidget(scrollable_container)
        layout.setContentsMargins(3, 3, 3, 3)

        database_group.setLayout(layout)
        return database_group

    def create_toggables_database(self, database_path, container, same=False):
        """
        Toggables Database for specified path
        """
        selectables = []

        if same:
            selectables = [container.widget().layout().itemAt(i).widget()
                           for i in range(container.widget().layout().count())]
        else:
            for i in range(container.widget().layout().count()):
                container.widget().layout().itemAt(i).widget().close()
        folders = [widget.text() for widget in selectables]

        if not os.path.exists(database_path):
            return selectables

        for folder in [f.path for f in os.scandir(database_path) if f.is_dir() and any('.pbz2' in _file for _file in os.listdir(f.path))]:
            name = os.path.normpath(folder).split(os.path.sep)[-1]
            if name not in folders:
                selectables.append(QtWidgets.QCheckBox(name))
                selectables[-1].setChecked(False)
                selectables[-1].toggled.connect(self.select_one)
                container.widget().layout().addWidget(selectables[-1])
        return selectables

    def select_all(self, state):
        """
        Deal with Select All
        """
        if self.left_group_box:
            checkboxes = [child for child in self.left_group_box.children(
            )[2].widget().children() if isinstance(child, QtWidgets.QCheckBox)]
            if state == 2:
                _ = [check.setChecked(True) for check in checkboxes]
            elif state == 0:
                _ = [check.setChecked(False) for check in checkboxes]

    def select_one(self, checked):
        """
        Deal with checkboxes
        """
        if self.left_group_box:
            states = [child.checkState() for child in self.left_group_box.children(
            )[2].widget().children() if isinstance(child, QtWidgets.QCheckBox)]
            if checked and all(state == 2 for state in states):
                self.left_group_box.children()[1].setCheckState(2)
            elif not checked and all(state == 0 for state in states):
                self.left_group_box.children()[1].setCheckState(0)
            else:
                self.left_group_box.children()[1].setCheckState(1)

    def click_pass_semi(self, clicked):
        """
        Deal with semi_state on clicking on Select All
        """
        if self.left_group_box:
            if clicked and self.left_group_box.children()[1].checkState() == 1:
                self.left_group_box.children()[1].setCheckState(2)

    def create_add_your_own_group(self):
        """
        Add Your Own Group
        """
        add_your_own = QtWidgets.QGroupBox("Add Your Own")

        layout = QtWidgets.QGridLayout()

        buttons_layer = QtWidgets.QHBoxLayout()

        button = QtWidgets.QPushButton('Choose Files')
        button.clicked.connect(self.open_filenames_dialog)
        buttons_layer.addWidget(button)

        button = QtWidgets.QPushButton('Parse')
        button.clicked.connect(self.parse_files)
        button.setVisible(False)
        buttons_layer.addWidget(button)

        layout.addItem(buttons_layer)

        progressBar = QtWidgets.QProgressBar()
        progressBar.setRange(0, 100)
        progressBar.setValue(0)
        progressBar.setVisible(False)
        layout.addWidget(progressBar)

        scrollable_container = self.create_container_files()
        layout.addWidget(scrollable_container)

        layout.setContentsMargins(1, 1, 1, 1)

        add_your_own.setLayout(layout)
        return add_your_own

    def create_container_files(self):
        """
        Scrollable container
        """
        container = QtWidgets.QWidget()

        container_layout = QtWidgets.QVBoxLayout()
        container_layout.setAlignment(QtCore.Qt.AlignTop)
        container.setLayout(container_layout)

        # Scroll Area Properties.
        scroll = QtWidgets.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def open_filenames_dialog(self):
        """
        Open File Dialog for adding
        """
        self.right_group_box.children()[3].setVisible(False)
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "", "MusicXML Files (*.mxl *.xml)", options=options)
        if files:
            self.right_group_box.children()[2].setVisible(True)
            for filename in files:
                if not filename in self.files_to_parse:
                    self.files_to_parse.append(filename)
                    file_n = os.path.normpath(filename).split(os.path.sep)[-1]
                    self.right_group_box.children()[4].widget(
                    ).layout().addWidget(OnOffWidget(file_n))

    def parse_files(self):
        """
        Parse Files
        """
        self.increase_progress_bar(0)
        _ = [child.btn_del.setEnabled(False) for child in self.right_group_box.children(
        )[4].widget().children() if isinstance(child, OnOffWidget)]

        application = self.parentWidget().parentWidget().application
        worker = Worker(
            application.parse_files, self.files_to_parse, self)
        worker.signals.finished.connect(self.stop_waiting)
        self.threadpool.start(worker)
        self.start_waiting()


    def handler_finish_parsing(self, value):
        """
        Finish Parsing Sequences
        """
        application = self.parentWidget().parentWidget().application
        self.create_toggables_database(
            application.database_path, self.left_group_box.children()[2], same=True)

    def increase_progress_bar(self, value):
        """
        """
        self.right_group_box.children()[3].setVisible(True)
        self.right_group_box.children()[3].setValue(value)

        if value >= 100:
            _ = [child.on_delete() for child in self.right_group_box.children(
            )[4].widget().children() if isinstance(child, OnOffWidget)]

    def next(self):
        """
        To Override
        """
        checkboxes = [child for child in self.left_group_box.children(
        )[2].widget().children() if isinstance(child, QtWidgets.QCheckBox)]
        folders = [checkbox.text()
                   for checkbox in checkboxes if checkbox.checkState() == 2]

        application = self.parentWidget().parentWidget().application

        worker_1 = Worker(application.retrieve_database, folders)
        worker_1.signals.finished.connect(self.stop_waiting_next)
        self.threadpool.start(worker_1)
        self.start_waiting()
