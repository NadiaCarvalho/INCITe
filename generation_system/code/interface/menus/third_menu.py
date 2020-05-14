"""
Main Window for Interface
"""

import sys

from PyQt5 import Qt, QtGui, QtWidgets

from interface.menus.menu import MyMenu

class ThirdMenu(MyMenu):
    """
    Third Menu:
    - Choosing 
    """
    def __init__(self, width, height, *args, **kwargs):
        super(ThirdMenu, self).__init__(width, height, *args, **kwargs)
        self.setStyleSheet("""background: red;""")