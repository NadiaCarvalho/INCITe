"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from interface.menus.menu import MyMenu

class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
class ShowStatsWidget(QtWidgets.QWidget):
    def __init__(self, name, statistics):
        super(ShowStatsWidget, self).__init__()

        self.name = name
        self.statistics = statistics
        self.weight = 1

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setAlignment(QtCore.Qt.AlignTop)
        self.vbox.setContentsMargins(5, 5, 5, 5)

        self.lbl = QtWidgets.QLabel("\n".join(self.name.split('.')))
        self.lbl.setStyleSheet("""color: blue; font: bold 20px;""")
        self.vbox.addWidget(self.lbl)   # Add the label to the layout

        for key, stat in self.statistics.items():
            if isinstance(stat, list):
                plus_text = ''
                s_label = QtWidgets.QLabel('')
                if key == 'unique_values' and len(stat) < 5:
                    for _tuple in stat:
                        plus_text += str(_tuple[0]) + ' : ' + \
                            str(_tuple[1]) + ' times\n'
                elif key == 'unique_percentages' and len(stat) < 5:
                    for perc in stat:
                        plus_text += str(perc) + ' %\n'
                if plus_text != '':
                    s_label.setText(''.join(key.split('_')) +
                                    ' : ' + '\n' + plus_text)
                    self.vbox.addWidget(s_label)
            else:
                s_label = QtWidgets.QLabel(
                    ''.join(key.split('_')) + ' : ' + str(stat))
                s_label.setWordWrap(True)
                if 'percentage' in key:
                    s_label.setText(s_label.text() + ' %')

                self.vbox.addWidget(s_label)

        line_splitter = QHLine()
        self.vbox.addWidget(line_splitter)

        if 'weight' in self.statistics:
            self.weight = self.statistics['weight']

        label = QtWidgets.QLabel('Choose Weight: ')
        label.setStyleSheet("""color: blue; font: bold 18px; margin-top: 5px""")
        self.vbox.addWidget(label)

        self.weight_box = QtWidgets.QSpinBox(self)
        self.weight_box.setValue(self.weight)
        self.weight_box.setStyleSheet("""color: blue; font: bold 18px; background: white""")
        self.weight_box.valueChanged.connect(self.change_weight)
        self.vbox.addWidget(self.weight_box)

        self.setLayout(self.vbox)

    def change_weight(self, value):
        """
        Handle for spinbox of weight
        """
        self.weight = value


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
        if self.container.layout() is not None:
            for i in range(self.container.layout().count()):
                self.container.layout().itemAt(i).widget().close()

        # Initialize tab screen
        tabs = QtWidgets.QTabWidget()
        tab_parts = self.create_statistics_folder(statistics['parts'], tabs)
        tab_vert = self.create_statistics_folder(statistics['vert'], tabs)

        # Add tabs
        tabs.addTab(tab_parts, "Part Events")
        tabs.addTab(tab_vert, "Vertical Events")

        # Add tabs to widget
        self.container.layout().addWidget(tabs)

    def create_statistics_folder(self, statistics, tabs):
        """
        """
        main_widget = QtWidgets.QWidget()

        # Create first tab
        main_widget.setLayout(QtWidgets.QGridLayout(tabs))

        information_view = QtWidgets.QStackedWidget()
        list_wid = QtWidgets.QListWidget()
        list_wid.currentRowChanged.connect(
            lambda i: information_view.setCurrentIndex(i))

        for key, stat in statistics.items():
            list_wid.addItem(key)
            information_view.addWidget(ShowStatsWidget(key, stat))

        information_view.setCurrentIndex(10)
        main_widget.layout().addWidget(list_wid, 0, 0, 1, 1)
        main_widget.layout().addWidget(information_view, 0, 1, 1, 1)
        return main_widget

    def next(self):
        """
        To Override
        """
        weights_dict = {
            'part': {},
            'vert': {},
        }

        print(self.container.children()[1].children()[0].children()[1])
        part_widget = self.container.children()[1].children()[0].children()[1].children()[2]
        for i in range(part_widget.count()):
            widget = part_widget.widget(i)
            if isinstance(widget, ShowStatsWidget):
                weights_dict['part'][widget.name] = widget.weight

        vert_widget = self.container.children()[1].children()[0].children()[2].children()[2]
        for i in range(vert_widget.count()):
            widget = vert_widget.widget(i)
            if isinstance(widget, ShowStatsWidget):
                weights_dict['vert'][widget.name] = widget.weight


        self.parentWidget().parentWidget().application.apply_viewpoint_weights(weights_dict)
