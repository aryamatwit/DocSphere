# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) James H, Manas A, Aakash M
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Spyder DevSphere Plugin."""
from ._version import __version__

# The following statements are required to register this 3rd party plugin:

from .devsphereplugin import DevSpherePlugin

PLUGIN_CLASS = DevSpherePlugin
