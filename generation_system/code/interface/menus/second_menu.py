"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from interface.menus.menu import MyMenu
from representation.events.viewpoint_description import DESCRIPTION


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class ShowStatsWidget(QtWidgets.QWidget):
    def __init__(self, name, statistics, description):
        super(ShowStatsWidget, self).__init__()

        self.name = name

        self.description = description

        self.weight = 0
        self.is_fixed = False

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setAlignment(QtCore.Qt.AlignTop)
        self.vbox.setContentsMargins(5, 5, 5, 5)

        splited_name = self.name.split('.')

        if len(splited_name) > 2:
            part = " -> ".join(splited_name[0:2])
            new_part = " -> ".join(splited_name[2:])
            self.lbl = QtWidgets.QLabel("\n-> ".join([part, new_part]))
        else:
            self.lbl = QtWidgets.QLabel(" -> ".join(splited_name))

        self.lbl.setStyleSheet("""color: blue; font: bold 18px;""")
        self.vbox.addWidget(self.lbl)   # Add the label to the layout

        self.lbl_2 = QtWidgets.QLabel(self.description)
        self.lbl_2.setStyleSheet("""color: black; font: bold 15px;""")
        self.vbox.addWidget(self.lbl_2)   # Add the label to the layout

        line_splitter = QHLine()
        self.vbox.addWidget(line_splitter)

        for key, stat in statistics.items():
            if key == 'weight':
                self.weight = stat
            elif key == 'fixed':
                self.is_fixed = stat
            else:
                self.vbox.addWidget(self.handle_stat(
                    key, stat, QtWidgets.QLabel('')))

        line_splitter = QHLine()
        self.vbox.addWidget(line_splitter)

        label = QtWidgets.QLabel('Choose Weight: ')
        label.setStyleSheet(
            """color: blue; font: bold 18px; margin-top: 5px""")
        self.vbox.addWidget(label)

        self.weight_box = QtWidgets.QSpinBox(self)
        self.weight_box.setMaximum(100)
        self.weight_box.setFixedWidth(100)
        self.weight_box.setValue(self.weight)
        self.weight_box.setStyleSheet(
            """color: blue; font: bold 18px;""")
        self.weight_box.valueChanged.connect(self.change_weight)
        self.vbox.addWidget(self.weight_box)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignTop)
        hbox.setContentsMargins(5, 5, 5, 5)

        f_label = QtWidgets.QLabel('Fixed Weight ?')
        f_label.setStyleSheet(
            """color: blue; font: bold 18px;""")

        self.fixed_box = QtWidgets.QCheckBox(self)
        # self.fixed_box.setStyleSheet(
        #     """QCheckBox::indicator
        #         {
        #         border : 1px solid black;
        #         width : 20px;
        #         height : 20px;
        #         background: white;
        #         color: blue;
        #         font: bold 18px;
        #         }""")
        self.fixed_box.stateChanged.connect(self.change_fixed_status)

        f_label.setBuddy(self.fixed_box)
        hbox.addWidget(f_label)
        hbox.addWidget(self.fixed_box)

        self.vbox.addLayout(hbox)

        self.setLayout(self.vbox)

    def change_weight(self, value):
        """
        Handle for spinbox of weight
        """
        self.weight = value

    def change_fixed_status(self, state):
        """
        Handle for checkbox of fixed weight
        """
        self.is_fixed = (False, True)[state == 2]
        self.weight_box.setDisabled(self.is_fixed)

    def handle_stat(self, key, stat, label):
        """
        Handle statistics labeling
        """
        if isinstance(stat, list):
            plus_text = ''
            if key == 'unique_values' and len(stat) < 5:
                for _tuple in stat:
                    plus_text += str(_tuple[0]) + ' : ' + \
                        str(_tuple[1]) + ' times\n'
            elif key == 'unique_percentages' and len(stat) < 5:
                for perc in stat:
                    plus_text += str(perc) + ' %\n'

            if plus_text != '':
                label.setText(' '.join(key.split('_')) +
                              ' : ' + '\n' + plus_text)
        else:
            label.setText(' '.join(key.split('_')) + ' : ' + str(stat))
            label.setWordWrap(True)
            if 'percentage' in key:
                label.setText(label.text() + ' %')

        return label

    def change_stats(self, stats):
        if 'weight' in stats:
            self.weight_box.setValue(stats['weight'])
        if 'fixed' in stats:
            self.fixed_box.setChecked(stats['fixed'])

        for widget in self.children():
            if isinstance(widget, QtWidgets.QLabel):
                if ' : ' in widget.text():
                    key = '_'.join(widget.text().split(' : ')[0].split(' '))
                    widget = self.handle_stat(key, stats[key], widget)


class SecondMenu(MyMenu):
    """
    Second Menu:
    - Present Statistics
    - Choosing Weights
    """

    def __init__(self, width, height, parent, *args, **kwargs):
        super(SecondMenu, self).__init__(
            width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: light gray;""")

        self.top_group = self.create_settings(parent, width)
        self.top_group.layout().setContentsMargins(5, 5, 10, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(QtWidgets.QVBoxLayout(self.container))
        self.container.layout().setContentsMargins(5, 5, 5, 5)
        self.tab_parts = None
        self.tab_vertical = None

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

        button = QtWidgets.QPushButton('View Automatic Viewpoints')
        button.clicked.connect(self.calculate_automatic_weights)
        layout.addWidget(button, 0, 1, 1, 1)

        database_group.setLayout(layout)
        return database_group

    def calculate_statistics(self):
        """
        Calculate satistics for music
        """
        self.parentWidget().parentWidget().application.calculate_statistics(self)

    def calculate_automatic_weights(self):
        """
        Calculate satistics for music
        """
        self.parentWidget().parentWidget().application.calculate_statistics(
            self, calc_weights=True)

    def create_statistics_overview(self, statistics):
        """
        Receive signal for presenting statistics
        """
        if self.tab_parts is not None:
            part_widget = self.tab_parts.children()[2]
            for i in range(part_widget.count()):
                widget = part_widget.widget(i)
                if isinstance(widget, ShowStatsWidget):
                    widget.change_stats(
                        list(statistics['parts'].items())[i][1])

        if self.tab_vertical is not None:
            vertical_widget = self.tab_vertical.children()[2]
            for i in range(vertical_widget.count()):
                widget = vertical_widget.widget(i)
                if isinstance(widget, ShowStatsWidget):
                    widget.change_stats(
                        list(statistics['vertical'].items())[i][1])

        if self.tab_parts is None and self.tab_vertical is None:
            # Initialize tab screen
            tabs = QtWidgets.QTabWidget()
            self.tab_parts = self.create_statistics_folder('parts',
                statistics['parts'], tabs)
            self.tab_vertical = self.create_statistics_folder('vertical',
                statistics['vertical'], tabs)

            # Add tabs
            tabs.addTab(self.tab_parts, "Part Events")
            tabs.addTab(self.tab_vertical, "Vertical Events")

            # Add tabs to widget
            self.container.layout().addWidget(tabs)

    def create_statistics_folder(self, type, statistics, tabs):
        """
        """
        main_widget = QtWidgets.QWidget()

        # Create first tab
        main_widget.setLayout(QtWidgets.QGridLayout(tabs))

        information_view = QtWidgets.QStackedWidget()
        list_wid = QtWidgets.QListWidget()
        list_wid.currentRowChanged.connect(
            lambda i: information_view.setCurrentIndex(i))

        for key, description in DESCRIPTION[type].items():
            if key in statistics:
                list_wid.addItem(key)
                information_view.addWidget(ShowStatsWidget(key, statistics[key], description))

        information_view.setCurrentIndex(10)
        main_widget.layout().addWidget(list_wid, 0, 0, 1, 1)
        main_widget.layout().addWidget(information_view, 0, 1, 1, 1)
        return main_widget

    def next(self):
        """
        To Override
        """
        weights_dict = {
            'parts': {},
            'vertical': {},
        }

        fixed_dict = {
            'parts': {},
            'vertical': {},
        }

        if self.tab_parts:
            part_widget = self.tab_parts.children()[2]
            for i in range(part_widget.count()):
                widget = part_widget.widget(i)
                if isinstance(widget, ShowStatsWidget):
                    weights_dict['parts'][widget.name] = widget.weight
                    fixed_dict['parts'][widget.name] = widget.is_fixed

        if self.tab_vertical:
            vertical_widget = self.tab_vertical.children()[2]
            for i in range(vertical_widget.count()):
                widget = vertical_widget.widget(i)
                if isinstance(widget, ShowStatsWidget):
                    weights_dict['vertical'][widget.name] = widget.weight
                    fixed_dict['vertical'][widget.name] = widget.is_fixed

        main_window = self.parentWidget().parentWidget()
        main_window.application.apply_viewpoint_weights(weights_dict, fixed_dict)
        main_window.wids[main_window.front_wid + 1].set_maximum_spinbox()
