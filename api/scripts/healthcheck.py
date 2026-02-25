"""Docker healthcheck script that checks the /health endpoint."""

import sys
import urllib.request


def main() -> None:
    try:
        req = urllib.request.Request("http://localhost:3456/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                sys.exit(0)
    except Exception:
        pass
    sys.exit(1)


if __name__ == "__main__":
    main()
