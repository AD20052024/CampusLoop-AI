import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "http://127.0.0.1:8000/"
HEALTH_URL = "http://127.0.0.1:8000/health"


def server_is_ready() -> bool:
    try:
        with urlopen(HEALTH_URL, timeout=1) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def main() -> int:
    if not server_is_ready():
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=PROJECT_ROOT,
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )

        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if server_is_ready():
                break
            time.sleep(0.4)
        else:
            print("CampusLoop did not start. Check the server window for errors.")
            return 1

    webbrowser.open(SITE_URL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())