# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) James H, Manas A, Aakash M
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""DevSphere Widget."""
# Third party imports
from qtpy.QtWidgets import QWidget


class DevSphereWidget(QWidget):
    """DevSphere widget."""
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.setWindowTitle("DevSphere")
