from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

# Palette da fotocopia di fanzine, la stessa di ASD.
TONER = "#0B0B0B"
ASPHALT = "#1A1A1A"
CONCRETE = "#2A2A2A"
PAPER = "#EDE8DA"
SMUDGE = "#8A877E"
ACID = "#D7FF1F"
SPRAY = "#FF2B2B"

ASSETS = Path(__file__).resolve().parent / "assets"


def _first_family(candidates: tuple[str, ...], fallback: QFontDatabase.SystemFont) -> str:
    families = set(QFontDatabase.families())
    for name in candidates:
        if name in families:
            return name
    return QFontDatabase.systemFont(fallback).family()


class Fonts:
    stencil = "sans-serif"
    typewriter = "monospace"

    @classmethod
    def load(cls):
        cls.stencil = _first_family(
            ("Arial Black", "Impact", "Archivo Black", "DejaVu Sans", "Ubuntu", "Segoe UI"),
            QFontDatabase.SystemFont.TitleFont,
        )
        cls.typewriter = _first_family(
            ("Courier Prime", "Courier New", "Consolas", "Ubuntu Mono", "DejaVu Sans Mono", "Liberation Mono"),
            QFontDatabase.SystemFont.FixedFont,
        )


def stylesheet() -> str:
    s, t = Fonts.stencil, Fonts.typewriter
    arrow = (ASSETS / "arrow.svg").as_posix()
    return f"""
* {{ font-family: "{t}"; font-size: 13px; color: {PAPER}; outline: 0; }}
QMainWindow, QWidget#root, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget {{ background: {TONER}; }}
QToolTip {{ background: {ACID}; color: {TONER}; border: 2px solid {TONER}; padding: 4px; }}

QLabel#display {{ font-family: "{s}"; font-weight: 900; font-size: 46px; letter-spacing: -2px; color: {PAPER}; }}
QLabel#headline {{ font-family: "{s}"; font-weight: 900; font-size: 22px; color: {PAPER}; }}
QLabel#title {{ font-family: "{s}"; font-weight: 800; font-size: 15px; color: {PAPER}; }}
QLabel#label {{ font-weight: bold; font-size: 12px; letter-spacing: 1px; color: {ACID}; }}
QLabel#muted, QLabel#meta {{ color: {SMUDGE}; font-size: 12px; }}
QLabel#index {{ font-weight: bold; font-size: 11px; color: {SPRAY}; }}
QLabel#ok {{ font-weight: bold; font-size: 11px; letter-spacing: 1px; color: {ACID}; }}
QLabel#bad {{ font-weight: bold; font-size: 11px; letter-spacing: 1px; color: {SPRAY}; }}
QLabel#stamp {{ font-weight: bold; font-size: 12px; letter-spacing: 1px; color: {SPRAY}; border: 2px solid {SPRAY}; padding: 2px 8px; }}
QLabel a {{ color: {ACID}; }}

QFrame#rule {{ background: {PAPER}; max-height: 2px; min-height: 2px; }}
QFrame#card {{ background: {TONER}; border: 2px solid {CONCRETE}; }}
QFrame#card[failed="true"] {{ border-color: {SPRAY}; }}
QFrame#card[done="true"] {{ border-color: {ACID}; }}
QFrame#service {{ background: {ASPHALT}; border: 2px solid {CONCRETE}; }}
QFrame#service:hover {{ border-color: {ACID}; }}

QPushButton#tab {{ background: {TONER}; color: {PAPER}; border: none; font-weight: bold; font-size: 13px;
    letter-spacing: 2px; min-height: 48px; padding: 0 18px; }}
QPushButton#tab:hover {{ background: {ASPHALT}; }}
QPushButton#tab:checked {{ background: {ACID}; color: {TONER}; }}

QPushButton#chip {{ background: transparent; color: {PAPER}; border: 2px solid {SMUDGE}; padding: 6px 12px;
    font-weight: bold; font-size: 12px; letter-spacing: 1px; }}
QPushButton#chip:hover {{ border-color: {PAPER}; }}
QPushButton#chip:checked {{ background: {ACID}; color: {TONER}; border-color: {ACID}; }}

QPushButton#link {{ background: transparent; border: none; color: {PAPER}; font-weight: bold; font-size: 12px;
    letter-spacing: 1px; padding: 4px 2px; text-align: left; }}
QPushButton#link:hover {{ color: {ACID}; }}
QPushButton#link:disabled {{ color: {CONCRETE}; }}
QPushButton#danger {{ background: transparent; border: none; color: {SPRAY}; font-weight: bold; font-size: 12px;
    letter-spacing: 1px; padding: 4px 2px; }}

QLineEdit, QPlainTextEdit, QSpinBox, QComboBox {{ background: {TONER}; border: 2px solid {PAPER}; padding: 8px;
    selection-background-color: {ACID}; selection-color: {TONER}; font-size: 14px; }}
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{ border-color: {ACID}; }}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{ border-color: {CONCRETE}; color: {SMUDGE}; }}
QPlainTextEdit {{ font-size: 14px; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{ image: url("{arrow}"); width: 12px; height: 8px; }}
QComboBox QAbstractItemView {{ background: {ASPHALT}; border: 2px solid {ACID}; selection-background-color: {ACID};
    selection-color: {TONER}; padding: 2px; }}
QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: none; }}

QCheckBox {{ spacing: 10px; font-size: 13px; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {PAPER}; background: {TONER}; }}
QCheckBox::indicator:checked {{ background: {ACID}; border-color: {ACID}; }}
QCheckBox:disabled {{ color: {SMUDGE}; }}
QCheckBox::indicator:disabled {{ border-color: {CONCRETE}; }}

QProgressBar {{ background: {CONCRETE}; border: none; max-height: 6px; min-height: 6px; }}
QProgressBar::chunk {{ background: {ACID}; }}

QScrollBar:vertical {{ background: {TONER}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {CONCRETE}; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {ACID}; }}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{ height: 0; background: none; }}
QMessageBox {{ background: {ASPHALT}; }}
QMessageBox QPushButton, QDialogButtonBox QPushButton {{ background: {ACID}; color: {TONER}; border: 2px solid {TONER};
    padding: 6px 16px; font-weight: bold; }}
"""


class PunkButton(QPushButton):
    """Bottone pieno con ombra netta sfalsata: niente ripple morbidi, solo blocchi."""

    SHADOW = 5

    def __init__(self, text: str, parent: QWidget | None = None, *, fill: str = ACID, ink: str = TONER,
                 shadow: str = SPRAY, big: bool = False):
        super().__init__(text, parent)
        self.fill, self.ink, self.shadow = QColor(fill), QColor(ink), QColor(shadow)
        self.big = big
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")

    def _font(self) -> QFont:
        f = QFont(Fonts.typewriter if not self.big else Fonts.stencil)
        f.setBold(True)
        f.setWeight(QFont.Weight.Black if self.big else QFont.Weight.Bold)
        f.setPixelSize(20 if self.big else 13)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2 if self.big else 1)
        return f

    def sizeHint(self) -> QSize:
        from PySide6.QtGui import QFontMetrics

        fm = QFontMetrics(self._font())
        pad_x, pad_y = (28, 16) if self.big else (16, 11)
        w = fm.horizontalAdvance(self.text().upper()) + 2 * pad_x + self.SHADOW
        h = fm.height() + 2 * pad_y + self.SHADOW
        return QSize(w, h)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def paintEvent(self, _):
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(0, 0, -self.SHADOW, -self.SHADOW)
        enabled = self.isEnabled()
        pressed = self.isDown()
        off = self.SHADOW if pressed else 0
        if not pressed:
            p.fillRect(r.translated(self.SHADOW, self.SHADOW), self.shadow if enabled else QColor(CONCRETE))
        body = r.translated(off, off)
        fill = self.fill if enabled else QColor(CONCRETE)
        if enabled and self.underMouse() and not pressed:
            fill = fill.lighter(108)
        p.fillRect(body, fill)
        p.setPen(QPen(QColor(TONER), 2))
        p.drawRect(body.adjusted(1, 1, -1, -1))
        p.setPen(self.ink if enabled else QColor(SMUDGE))
        p.setFont(self._font())
        p.drawText(body, Qt.AlignmentFlag.AlignCenter, self.text().upper())


class Mark(QWidget):
    """Il marchio: freccia di download che sfonda il cerchio, come la A di ASD."""

    def __init__(self, size: int = 56, variant: str = "mark", parent: QWidget | None = None):
        super().__init__(parent)
        self.renderer = QSvgRenderer(str(ASSETS / f"{variant}.svg"), self)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.renderer.render(p, QRectF(self.rect()))


def app_icon() -> QIcon:
    return QIcon(str(ASSETS / "icon.svg"))


def label(text: str, name: str = "label") -> QLabel:
    w = QLabel(text)
    w.setObjectName(name)
    return w
