#!/usr/bin/env python3.7
"""
This script presents the class Viewpoint that represents a specific Viewpoint and its information
"""


class Viewpoint:
    """
    Class Viewpoint # τ
    """

    def __init__(self, name, info):
        self.name = name
        self.info = info

    def get_name(self):
        """
        Returns the viewpoint's name
        """
        return self.name

    def get_info(self):
        """
        Returns the viewpoint's information
        """
        return self.info

    def partial_function(self):  # , event):
        """
        Returns the viewpoint's partial_function # Ψ[τ](event)
        """
        return self

    def coversion_surface_string(self):  # , event):
        """
        Returns the viewpoint's coversion_surface_string # Φ[τ](event)
        """
        return self

    def __str__(self):
        """
        Overrides str function for Viewpoint
        """
        return 'Viewpoint {}: {} \n'.format(self.name, self.info)
    
    def __eq__(self, other):
        """
        Overrides equal function for Viewpoint
        """
        return (other is not None and self.name == other.get_name() and self.info == other.get_info())

    def __ne__(self, other):
        """
        Overrides non-equal function for Viewpoint
        """
        return not self == other