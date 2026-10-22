"""
Lion City Capital (fictitious) - an end-to-end algorithmic trading pipeline.

Learners build this package stage by stage, one module per lab, and run every
stage from the labs folder with one CLI:

    python -m pipeline                 # list the stages
    python -m pipeline check           # Lab 01  configuration + paper account
    python -m pipeline e2e --yes       # Lab 20  the whole pipeline, end to end

PAPER TRADING ONLY. There is no live-trading code path: every Alpaca client is
created with paper=True and the offline simulator never touches a broker.
Not investment advice.
"""

__version__ = "1.0.0"
