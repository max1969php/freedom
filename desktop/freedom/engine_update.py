from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

PYPI_URL = "https://pypi.org/pypi/yt-dlp/json"


def data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return base / "Freedom"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "freedom"


def engine_dir() -> Path:
    return data_dir() / "engine"


def bootstrap() -> None:
    """Da chiamare prima di importare yt_dlp: se c'è un motore aggiornato, ha la precedenza."""
    current = engine_dir() / "current"
    if (current / "yt_dlp" / "__init__.py").exists():
        sys.path.insert(0, str(current))


def installed_version() -> str:
    import yt_dlp.version

    return yt_dlp.version.__version__


def latest_release(timeout: float = 15) -> tuple[str, str, str]:
    with urllib.request.urlopen(PYPI_URL, timeout=timeout) as r:
        info = json.load(r)
    version = info["info"]["version"]
    for f in info["urls"]:
        if f["packagetype"] == "bdist_wheel" and f["filename"].endswith("py3-none-any.whl"):
            return version, f["url"], f["digests"]["sha256"]
    raise RuntimeError("Nessuna wheel di yt-dlp trovata su PyPI")


def update(timeout: float = 60) -> str | None:
    """Scarica l'ultima yt-dlp se più nuova. Restituisce la nuova versione, o None se già aggiornato."""
    version, url, sha256 = latest_release()
    if version == installed_version():
        return None
    root = engine_dir()
    root.mkdir(parents=True, exist_ok=True)
    wheel = root / "download.whl"
    with urllib.request.urlopen(url, timeout=timeout) as r, open(wheel, "wb") as out:
        shutil.copyfileobj(r, out)
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    if digest != sha256:
        wheel.unlink(missing_ok=True)
        raise RuntimeError("Checksum della wheel non valido: aggiornamento annullato")
    staging = root / f"v{version}"
    shutil.rmtree(staging, ignore_errors=True)
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            target = (staging / name).resolve()
            if not target.is_relative_to(staging.resolve()):
                raise RuntimeError("Wheel con percorsi non validi")
        z.extractall(staging)
    wheel.unlink(missing_ok=True)
    current = root / "current"
    shutil.rmtree(current, ignore_errors=True)
    staging.rename(current)
    return version
