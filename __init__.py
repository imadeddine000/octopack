"""
autodetect — Smart framework detection & Dockerfile generation.

Scans any project directory, detects the framework and language,
and generates a production-ready Dockerfile — zero dependencies,
pure Python stdlib.

Usage:
    python -m autodetect /path/to/project
    python -m autodetect /path/to/project --output Dockerfile
    python -m autodetect /path/to/project --json
"""

__version__ = "0.1.0"
