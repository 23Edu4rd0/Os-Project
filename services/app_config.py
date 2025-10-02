"""
app_config.py - Application configuration and setup

Handles logging, project paths, and warning suppression.
"""

import sys
import logging
import warnings
from pathlib import Path


def setup_warnings():
    """Suppress warnings for cleaner output."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)


def setup_logging():
    """Configure logging system for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def setup_project_root():
    """Setup project root directory in Python path."""
    root_dir = Path(__file__).resolve().parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    return root_dir


def initialize_config():
    """Initialize all configuration settings."""
    setup_warnings()
    logger = setup_logging()
    root_dir = setup_project_root()
    return logger, root_dir
