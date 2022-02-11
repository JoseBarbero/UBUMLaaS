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

from .ENN import ENN
from .CNN import CNN
# from .RNN import RNN
# from .MSS import MSS
# from .ICF import ICF
# from .DROP3 import DROP3

__all__ = ["ENN",
           "CNN"]
