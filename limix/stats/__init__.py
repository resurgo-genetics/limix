r"""
**********
Statistics
**********

- :func:`.pca`
- :func:`.boxcox`
- :func:`.gower_norm`
- :func:`.qvalues`
- :func:`.empirical_pvalues`
- :class:`.Chi2mixture`
- :func:`.indep_pairwise`

Public interface
^^^^^^^^^^^^^^^^
"""

from .pca import pca
from .trans import boxcox
from .kinship import gower_norm
from .fdr import qvalues
from .teststats import empirical_pvalues
from .chi2mixture import Chi2mixture
from .preprocess import indep_pairwise, maf

__all__ = ['pca', 'boxcox', 'gower_norm', 'qvalues',
           'empirical_pvalues', 'Chi2mixture', 'indep_pairwise', 'maf']
