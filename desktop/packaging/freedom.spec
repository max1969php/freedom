# PyInstaller: cartella unica (avvio veloce), senza console. Uso: pyinstaller packaging/freedom.spec
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).parent
win = sys.platform == "win32"
icon = ROOT / "build" / "icons" / ("freedom.ico" if win else "freedom-256.png")

binaries = []
vendor = ROOT / "vendor"
# FFmpeg solo su Windows (su Ubuntu è una dipendenza del .deb); Deno ovunque: serve a YouTube.
for name in ("ffmpeg.exe", "ffprobe.exe", "deno.exe") if win else ("deno",):
    if (vendor / name).exists():
        binaries.append((str(vendor / name), "."))

a = Analysis(
    [str(ROOT / "freedom" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=[(str(ROOT / "freedom" / "assets"), "freedom/assets")],
    hiddenimports=collect_submodules("yt_dlp") + ["PySide6.QtSvg"],
    excludes=["tkinter", "PySide6.QtWebEngineCore", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.Qt3DCore"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="freedom" if not win else "Freedom",
    console=False,
    icon=str(icon) if icon.exists() else None,
    version=str(ROOT / "packaging" / "windows" / "version.txt") if win else None,
)
coll = COLLECT(exe, a.binaries, a.datas, name="freedom")
