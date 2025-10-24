"""
Villager AI Framework - AI-driven cybersecurity automation
"""

__version__ = "0.2.1rc1"
__author__ = "Villager AI Team"

# Import core components
from . import config
from . import villager_visuals

# Make key components available at package level
__all__ = [
    'config',
    'villager_visuals'
]
