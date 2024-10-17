# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) James H, Manas A, Aakash M
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""DevSphere Plugin."""
from qtpy.QtWidgets import QVBoxLayout

from spyder.api.plugins import SpyderPluginWidget
from .widgets.devspheregui import DevSphereWidget


class DevSpherePlugin(SpyderPluginWidget):
    """DevSphere plugin."""
    CONF_SECTION = 'DevSphere'
    
    CONFIGWIDGET_CLASS = None
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        SpyderPluginWidget.__init__(self, parent)

        

        # Graphical view
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

    # --- SpyderPluginWidget API ----------------------------------------------
    def get_plugin_title(self):
        """Return widget title."""
        return "DevSphere"

    def get_focus_widget(self):
        """Return the widget to give focus to."""
        return self.widget

    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        # Define where the plugin is going to be tabified next to
        # As default, it will be tabbed next to the ipython console
        
        self.tabify(self.main.help)
        

    