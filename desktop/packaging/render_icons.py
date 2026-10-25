"""Rasterizza assets/icon.svg in PNG (Linux, Android) e ICO (Windows) usando Qt."""
import sys
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "icons"


def render(size: int) -> QImage:
    img = QImage(QSize(size, size), QImage.Format.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(str(ROOT / "freedom" / "assets" / "icon.svg")).render(p)
    p.end()
    return img


def main():
    QGuiApplication(["render"])
    OUT.mkdir(parents=True, exist_ok=True)
    for s in (16, 24, 32, 48, 64, 128, 256, 512):
        render(s).save(str(OUT / f"freedom-{s}.png"))
    if not render(256).save(str(OUT / "freedom.ico"), "ICO"):
        sys.exit("Plugin ICO di Qt non disponibile")
    print(OUT)


if __name__ == "__main__":
    main()
