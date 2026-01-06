"""Allow running facecrop as a module: python -m facecrop"""

import sys

from .cli import main

if __name__ == '__main__':
    sys.exit(main())
