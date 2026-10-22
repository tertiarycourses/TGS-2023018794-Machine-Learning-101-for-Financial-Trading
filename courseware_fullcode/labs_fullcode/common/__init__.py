"""Shared helpers for the Machine Learning 101 for Financial Trading labs.

Every lab script adds labs/ to sys.path and then does e.g.
    from common.data import get_bars
"""

import warnings

# numpy 2.x on some macOS BLAS builds emits harmless "encountered in matmul" warnings
# from scikit-learn internals; hide them so learners see only meaningful output.
warnings.filterwarnings("ignore", message=".*encountered in matmul", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="Unknown solver options")   # scipy/sklearn version noise
