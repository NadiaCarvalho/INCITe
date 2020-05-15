"""
Main Window for Interface
"""

import os
import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from interface.menus.menu import MyMenu


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
        self.setStyleSheet("""background: gray;""")

        self.top_group = self.create_settings(parent)
        self.left_group_box = self.create_database_group(parent)
        self.right_group_box = self.create_add_your_own_group()

        self.main_layout.setRowStretch(1, 1)
        self.main_layout.setRowStretch(2, 15)
        self.main_layout.setRowStretch(3, 1)
        self.main_layout.setColumnStretch(0, 3)
        self.main_layout.setColumnStretch(1, 3)
        self.main_layout.setVerticalSpacing(2)
        self.main_layout.setContentsMargins(2, 5, 2, 5)

        self.main_layout.addWidget(self.top_group, 0, 0, 1, 3)
        self.main_layout.addWidget(self.left_group_box, 1, 0, 15, 0) # TODO: ver aqui
        self.main_layout.addWidget(self.right_group_box, 1, 1, 15, 3)

        self.files_to_parse = []
        self.database_selected = []

    def create_settings(self, parent):
        """
        """
        database_group = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)

        button = QtWidgets.QPushButton('Select Database Path')
        button.clicked.connect(self.database_path)
        layout.addWidget(button)

        label = QtWidgets.QLabel(parent.application.database_path)
        #label.setFixedWidth(200)
        label.setWordWrap(True)
        layout.addWidget(label)

        database_group.setLayout(layout)

        return database_group


    def database_path(self):
        """
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", options=options)

        if directory:
            application = self.parentWidget().parentWidget().application
            application.database_path = directory
            self.children()[2].children()[2].setText(directory)

            for i in range(self.left_group_box.children()[2].widget().layout().count()): 
                self.left_group_box.children()[2].widget().layout().itemAt(i).widget().close()

            self.create_toggables_database(directory, self.left_group_box.children()[2])

    def create_database_group(self, parent):
        """
        """
        database_group = QtWidgets.QGroupBox("Database")

        layout = QtWidgets.QVBoxLayout()

        check_box = QtWidgets.QCheckBox("Select All")
        check_box.setTristate(True)
        check_box.setCheckState(QtCore.Qt.Checked)

        layout.addWidget(check_box)

        scrollable_container = self.create_container_files()

        selectables = self.create_toggables_database(parent.application.database_path, scrollable_container)
        check_box.toggled.connect(lambda checked: checked and [
                            sel.setChecked(True) for sel in selectables])

        layout.addWidget(scrollable_container)
        layout.setContentsMargins(1, 1, 1, 1)

        database_group.setLayout(layout)
        return database_group

    def create_toggables_database(self, database_path, container):
        """
        """
        selectables = []
        for folder in [f.path for f in os.scandir(database_path) if f.is_dir() and any('.pbz2' in _file for _file in os.listdir(f.path))]:
            name = os.path.normpath(folder).split(os.path.sep)[-1]
            selectables.append(QtWidgets.QCheckBox(name))
            selectables[-1].setChecked(True)
            selectables[-1].toggled.connect(
                lambda checked: not checked and check_box.setChecked(QtCore.Qt.PartiallyChecked))
            container.widget().layout().addWidget(selectables[-1])
        return selectables

    def create_add_your_own_group(self):
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

        scrollable_container = self.create_container_files()
        layout.addWidget(scrollable_container)

        progressBar = QtWidgets.QProgressBar()
        progressBar.setRange(0, 10000)
        progressBar.setValue(0)
        progressBar.setVisible(False)
        layout.addWidget(progressBar)

        # timer = QTimer(self)
        # timer.timeout.connect(self.advanceProgressBar)
        # timer.start(1000)

        layout.setContentsMargins(1, 1, 1, 1)

        add_your_own.setLayout(layout)
        return add_your_own

    def create_container_files(self):
        container = QtWidgets.QWidget()

        container_layout = QtWidgets.QVBoxLayout()
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
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "", "MusicXML Files (*.mxl)", options=options)
        if files:
            self.right_group_box.children()[2].setVisible(True)
            for filename in files:
                if not filename in self.files_to_parse:
                    self.files_to_parse.append(filename)
                    file_n = os.path.normpath(filename).split(os.path.sep)[-1]
                    self.right_group_box.children()[3].widget(
                    ).layout().addWidget(OnOffWidget(file_n))

    def parse_files(self):
        """
        Parse Files
        """
        application = self.parentWidget().parentWidget().application
        application.parse_files(self.files_to_parse)

