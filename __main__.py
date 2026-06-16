"""
CLI entry point for ``python -m autodetect /path/to/project``.
"""

import json
import sys
from autodetect.cli import main

if __name__ == "__main__":
    sys.exit(main())
