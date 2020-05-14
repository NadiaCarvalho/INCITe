"""
Main caller for interface
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets

from interface.main_window import MainWindow

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
