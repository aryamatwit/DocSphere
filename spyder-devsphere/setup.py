# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) James H, Manas A, Aakash M
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Setup script for spyder_devsphere."""

# Standard library imports
import ast
import os

# Third party imports
from setuptools import find_packages, setup


HERE = os.path.abspath(os.path.dirname(__file__))


def get_description():
    """Get long description."""
    with open(os.path.join(HERE, 'README.rst'), 'r') as f:
        data = f.read()
    return data


REQUIREMENTS = ['spyder']


setup(
    name='spyder-devsphere',
    keywords=['Spyder', 'Plugin'],
    url='https://github.com/aakashmkj/spyder-devsphere',
    license='MIT',
    author='James H, Manas A, Aakash M',
    author_email='mukherjeea1@wit.edu',
    description='Real time collaborative code editor',
    long_description=get_description(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    package_data={'assets':['*']},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ])
