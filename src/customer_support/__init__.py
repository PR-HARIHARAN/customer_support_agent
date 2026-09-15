"""Customer-support agent: data prep, intent classification, and evaluation.

This package contains the reproducible small-sample pipeline. The notebooks
under ``notebooks/`` document the fuller experimental history (extraction,
EDA, conversation reconstruction, large-scale intent discovery).
"""

from .config import PilotConfig

__version__ = "0.2.0"
__all__ = ["PilotConfig", "__version__"]
