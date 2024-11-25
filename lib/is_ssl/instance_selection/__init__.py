#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    __init__.py.py
# @Author:      Daniel Puente Ramírez
# @Time:        16/11/21 17:14


"""
Instance Selection.

The package contains some of the most widely used instance selection algorithms
in the literature.
"""

__version__ = "0.1.3"
__author__ = 'Daniel Puente Ramírez'

from ._ENN import ENN
from ._CNN import CNN
from ._RNN import RNN
from ._MSS import MSS
from ._ICF import ICF
from ._DROP3 import DROP3

__all__ = ["ENN",
           "CNN",
           "RNN",
           "MSS",
           "ICF",
           "DROP3"]
