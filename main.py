
"""
main.py - Entry point for Merkava Service Order System

Features:
 - Tabbed interface for clients, orders, products, and backup
 - Window state and active tab persistence
 - Structured logging and global exception handling

Author: Eduardo Viana Chaves
License: MIT
"""

import sys
from services.app_runner import run_app


if __name__ == "__main__":
    sys.exit(run_app())