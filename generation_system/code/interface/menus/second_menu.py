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
        super(SecondMenu, self).__init__(width, height, parent, *args, **kwargs)
        self.setStyleSheet("""background: green;""")
