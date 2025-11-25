import sys
from contextlib import suppress
from typing import NoReturn


def main() -> NoReturn:
    from .server import mcp

    with suppress(KeyboardInterrupt):
        mcp.run()

    sys.exit()


if __name__ == "__main__":
    main()
