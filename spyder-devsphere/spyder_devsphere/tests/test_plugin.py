# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the plugin."""# Test library imports
import pytest

# Local imports
from spyder_devsphere.devsphereplugin import DevSpherePlugin
@pytest.fixture
def setup_devsphere(qtbot):
    """Set up the DevSpherePlugin plugin."""
    devsphere = DevSpherePlugin(None)
    qtbot.addWidget(devsphere)
    devsphere.show()
    return devsphere


def test_basic_initialization(qtbot):
    """Test DevSpherePlugin initialization."""
    devsphere = setup_devsphere(qtbot)

    # Assert that plugin object exist
    assert devsphere is not None


if __name__ == "__main__":
    pytest.main()
