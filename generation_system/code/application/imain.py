"""
Main caller for interface
"""

import sys

import PyQt5
from PyQt5 import Qt, QtGui, QtWidgets

from application.interface.main_window import MainWindow

def main():
    """
    Main Function for calling Interface
    """
    app = Qt.QApplication(sys.argv)
    app.setStyle('Fusion')

    music = ''
    if len(sys.argv) > 1:
        music = sys.argv[1]

    window = MainWindow(music=music)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()