"""允许通过 ``python -m numberpatterns`` 运行命令行工具。"""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
