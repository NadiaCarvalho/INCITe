"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets

from interface.menus.menu import MyMenu

class FirstMenu(MyMenu):
    """
    First Menu:
    - Choosing Database
    """
    def __init__(self, width, height, *args, **kwargs):
        super(FirstMenu, self).__init__(width, height, *args, **kwargs)
        self.setStyleSheet("""background: blue;""")
