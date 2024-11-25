"""
Common semi-supervised algorithms easily found in the literature.

Currently the following semi-supervised algorithm classification schemes are available in is-ssl:

+------------------------------------------------------+-----------------------------------------------------------+
| Classifier                                           | Description                                               |
+======================================================+===========================================================+
| :class:`~is_ssl.semisupervised.CoTraining`           | 
+------------------------------------------------------+-----------------------------------------------------------+
| :class:`~is_ssl.semisupervised.TriTraining`          |                                                           |
+------------------------------------------------------+-----------------------------------------------------------+
| :class:`~is_ssl.semisupervised.DemocraticCoLearning` |                                                           |
+------------------------------------------------------+-----------------------------------------------------------+

"""

from .semisupervised.CoTraining import CoTraining
from .semisupervised.TriTraining import TriTraining
from .semisupervised.DemocraticCoLearning import DemocraticCoLearning

__all__ = ["CoTraining",
           "TriTraining",
           "DemocraticCoLearning"]