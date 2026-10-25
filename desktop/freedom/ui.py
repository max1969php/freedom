from __future__ import annotations

import collections
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QSettings, QStandardPaths, Qt, QThreadPool, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSpinBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from . import __version__, engine_update
from .engine import FINISHED, DownloadManager, Job, State, open_path
from .i18n import LANGUAGES, set_language, tr
from .options import AUDIO_BITRATES, AUDIO_FORMATS, BROWSERS, QUALITIES, VIDEO_CONTAINERS, Mode, Request
from .sites import SERVICES, detect, split_urls
from .theme import Mark, PunkButton, label

REPO_URL = "https://github.com/max1969php/freedom"
SUPPORTED_URL = "https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md"


def _rule() -> QFrame:
    f = QFrame()
    f.setObjectName("rule")
    return f


def _btn(text: str, name: str = "link") -> QPushButton:
    b = QPushButton(text)
    b.setObjectName(name)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def _chip(text: str) -> QPushButton:
    b = _btn(text, "chip")
    b.setCheckable(True)
    return b


def _combo(items: list[tuple[str, object]], current: object) -> QComboBox:
    c = QComboBox()
    for text, data in items:
        c.addItem(text, data)
    i = c.findData(current)
    c.setCurrentIndex(max(0, i))
    return c


def _fmt_bytes(n: float | None) -> str:
    if not n:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}/s" if unit != "B" else f"{n:.0f} B/s"
        n /= 1024
    return f"{n:.1f} TB/s"


def _fmt_eta(s: int | None) -> str:
    if s is None:
        return ""
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


class Settings:
    def __init__(self):
        self.q = QSettings("Freedom", "Freedom")

    def get(self, key: str, default, kind=str):
        v = self.q.value(key, default)
        if kind is bool:
            return v if isinstance(v, bool) else str(v).lower() == "true"
        try:
            return kind(v)
        except (TypeError, ValueError):
            return default

    def set(self, key: str, value):
        self.q.setValue(key, value)

    @staticmethod
    def default_dir() -> str:
        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation) or str(Path.home())
        return str(Path(base) / "Freedom")


# ---------------------------------------------------------------- SCARICA

class DownloadPage(QWidget):
    submitted = Signal(list)

    def __init__(self, settings: Settings):
        super().__init__()
        self.s = settings
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        v = QVBoxLayout(body)
        v.setContentsMargins(28, 24, 28, 28)
        v.setSpacing(10)

        top = QHBoxLayout()
        top.addWidget(label("URL_"))
        top.addStretch()
        paste = _btn(tr("paste"))
        paste.clicked.connect(self._paste)
        clear = _btn(tr("clear"))
        top.addWidget(paste)
        top.addSpacing(14)
        top.addWidget(clear)
        v.addLayout(top)

        self.urls = QPlainTextEdit()
        self.urls.setPlaceholderText(tr("urls_placeholder"))
        self.urls.setMinimumHeight(120)
        self.urls.setMaximumHeight(200)
        self.urls.textChanged.connect(self._recognize)
        clear.clicked.connect(self.urls.clear)
        v.addWidget(self.urls)
        self.recognized = label("", "muted")
        self.recognized.setWordWrap(True)
        v.addWidget(self.recognized)

        v.addSpacing(8)
        v.addWidget(label(tr("what")))
        modes = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_chips: dict[Mode, QPushButton] = {}
        for mode, key in ((Mode.BOTH, "mode_both"), (Mode.VIDEO, "mode_video"), (Mode.AUDIO, "mode_audio")):
            chip = _chip(tr(key))
            self.mode_group.addButton(chip)
            self.mode_chips[mode] = chip
            modes.addWidget(chip)
            chip.toggled.connect(self._sync_mode)
        modes.addStretch()
        v.addLayout(modes)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        self.quality = _combo(
            [(tr("best") if q == 0 else f"{q}p", q) for q in QUALITIES], self.s.get("quality", 0, int)
        )
        self.container = _combo([(c.upper(), c) for c in VIDEO_CONTAINERS], self.s.get("container", "mp4"))
        self.audio_format = _combo(
            [(tr("original") if f == "best" else f.upper(), f) for f in AUDIO_FORMATS], self.s.get("audio_format", "mp3")
        )
        self.bitrate = _combo([(f"{b} kbps", b) for b in AUDIO_BITRATES], self.s.get("bitrate", "320"))
        self.q_label, self.c_label = label(tr("quality")), label(tr("container"))
        self.a_label, self.b_label = label(tr("audio_format")), label(tr("bitrate"))
        for col, (lab, w) in enumerate(
            ((self.q_label, self.quality), (self.c_label, self.container),
             (self.a_label, self.audio_format), (self.b_label, self.bitrate))
        ):
            grid.addWidget(lab, 0, col)
            grid.addWidget(w, 1, col)
        self.audio_format.currentIndexChanged.connect(self._sync_mode)
        v.addSpacing(6)
        v.addLayout(grid)

        v.addSpacing(10)
        v.addWidget(label(tr("compilation")))
        self.playlist = QCheckBox(tr("playlist_all"))
        self.playlist.setChecked(self.s.get("playlist", True, bool))
        v.addWidget(self.playlist)
        items_row = QHBoxLayout()
        self.items = QLineEdit()
        self.items.setPlaceholderText(tr("items_placeholder"))
        self.items.setMaximumWidth(320)
        items_row.addWidget(self.items)
        items_row.addWidget(label(tr("items_hint"), "muted"))
        items_row.addStretch()
        v.addLayout(items_row)
        self.playlist.toggled.connect(self.items.setEnabled)
        self.items.setEnabled(self.playlist.isChecked())

        v.addSpacing(10)
        v.addWidget(label(tr("extras")))
        extras = QHBoxLayout()
        self.subs = QCheckBox(tr("subtitles"))
        self.subs.setChecked(self.s.get("subtitles", False, bool))
        self.thumb = QCheckBox(tr("thumbnail"))
        self.thumb.setChecked(self.s.get("thumbnail", True, bool))
        self.meta = QCheckBox(tr("metadata"))
        self.meta.setChecked(self.s.get("metadata", True, bool))
        for w in (self.subs, self.thumb, self.meta):
            extras.addWidget(w)
            extras.addSpacing(18)
        extras.addStretch()
        v.addLayout(extras)

        v.addSpacing(10)
        v.addWidget(label(tr("save_in")))
        dest = QHBoxLayout()
        self.out_dir = QLineEdit(self.s.get("out_dir", Settings.default_dir()))
        browse = PunkButton(tr("browse"), fill="#EDE8DA", shadow="#D7FF1F")
        browse.clicked.connect(self._browse)
        dest.addWidget(self.out_dir, 1)
        dest.addSpacing(10)
        dest.addWidget(browse)
        v.addLayout(dest)

        v.addSpacing(18)
        go_row = QHBoxLayout()
        self.go = PunkButton(tr("download"), big=True)
        self.go.clicked.connect(self._submit)
        go_row.addWidget(self.go)
        go_row.addSpacing(18)
        self.hint = label(tr("rights"), "muted")
        self.hint.setWordWrap(True)
        go_row.addWidget(self.hint, 1)
        v.addLayout(go_row)
        v.addStretch()

        self.mode_chips[Mode(self.s.get("mode", Mode.BOTH.value))].setChecked(True)
        self._sync_mode()
        self._recognize()

    def mode(self) -> Mode:
        for m, chip in self.mode_chips.items():
            if chip.isChecked():
                return m
        return Mode.BOTH

    def _sync_mode(self):
        m = self.mode()
        video = m is not Mode.AUDIO
        for w in (self.q_label, self.quality):
            w.setVisible(video)
        for w in (self.c_label, self.container):
            w.setVisible(m is Mode.BOTH)
        for w in (self.a_label, self.audio_format):
            w.setVisible(not video)
        lossy = self.audio_format.currentData() not in ("flac", "wav", "best")
        for w in (self.b_label, self.bitrate):
            w.setVisible(not video and lossy)
        self.subs.setEnabled(video)

    def _recognize(self):
        urls = split_urls(self.urls.toPlainText())
        if not urls:
            self.recognized.setText(tr("recognized_none", n=len(SERVICES)))
            self.go.setEnabled(False)
            return
        counts = collections.Counter((detect(u).name if detect(u) else tr("other_site")) for u in urls)
        parts = [f"{name.upper()} ×{n}" for name, n in counts.most_common()]
        self.recognized.setText(tr("recognized", n=len(urls)) + "  " + " // ".join(parts))
        self.go.setEnabled(True)

    def _paste(self):
        text = QGuiApplication.clipboard().text().strip()
        if text:
            cur = self.urls.toPlainText().rstrip()
            self.urls.setPlainText((cur + "\n" if cur else "") + text)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, tr("save_in"), self.out_dir.text())
        if d:
            self.out_dir.setText(d)

    def add_urls(self, text: str):
        cur = self.urls.toPlainText().rstrip()
        self.urls.setPlainText((cur + "\n" if cur else "") + text.strip())

    def _submit(self):
        urls = split_urls(self.urls.toPlainText())
        if not urls:
            return
        out = self.out_dir.text().strip() or Settings.default_dir()
        s = self.s
        s.set("out_dir", out)
        s.set("mode", self.mode().value)
        s.set("quality", self.quality.currentData())
        s.set("container", self.container.currentData())
        s.set("audio_format", self.audio_format.currentData())
        s.set("bitrate", self.bitrate.currentData())
        s.set("playlist", self.playlist.isChecked())
        s.set("subtitles", self.subs.isChecked())
        s.set("thumbnail", self.thumb.isChecked())
        s.set("metadata", self.meta.isChecked())
        reqs = [
            Request(
                url=u, out_dir=out, mode=self.mode(), max_height=self.quality.currentData(),
                container=self.container.currentData(), audio_format=self.audio_format.currentData(),
                audio_bitrate=self.bitrate.currentData(), playlist=self.playlist.isChecked(),
                playlist_items=self.items.text(), subtitles=self.subs.isChecked(),
                embed_thumbnail=self.thumb.isChecked(), embed_metadata=self.meta.isChecked(),
                cookies_browser=s.get("cookies_browser", ""), cookies_file=s.get("cookies_file", ""),
                rate_limit=s.get("rate_limit", ""),
            )
            for u in urls
        ]
        self.urls.clear()
        self.items.clear()
        self.submitted.emit(reqs)


# ---------------------------------------------------------------- CODA

class JobCard(QFrame):
    def __init__(self, job: Job, manager: DownloadManager, number: int):
        super().__init__()
        self.setObjectName("card")
        self.job_id = job.id
        self.manager = manager
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(6)
        head = QHBoxLayout()
        idx = label(f"{number:03d}", "index")
        head.addWidget(idx, 0, Qt.AlignmentFlag.AlignTop)
        head.addSpacing(10)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.title = label("", "title")
        self.title.setWordWrap(True)
        self.meta = label("", "meta")
        self.meta.setWordWrap(True)
        col.addWidget(self.title)
        col.addWidget(self.meta)
        head.addLayout(col, 1)
        v.addLayout(head)
        self.status = label("", "ok")
        self.status.setWordWrap(True)
        v.addWidget(self.status)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setTextVisible(False)
        v.addWidget(self.bar)
        actions = QHBoxLayout()
        self.cancel = _btn(tr("cancel"), "danger")
        self.retry = _btn(tr("retry"))
        self.open = _btn(tr("open_folder"))
        self.remove = _btn(tr("remove"))
        for b in (self.cancel, self.retry, self.open, self.remove):
            actions.addWidget(b)
            actions.addSpacing(16)
        actions.addStretch()
        v.addLayout(actions)
        self.cancel.clicked.connect(lambda: manager.cancel(self.job_id))
        self.open.clicked.connect(self._open)
        self.refresh()

    def _open(self):
        job = self.manager.jobs.get(self.job_id)
        if not job:
            return
        target = Path(job.last_file).parent if job.last_file else Path(job.request.out_dir)
        open_path(str(target if target.exists() else job.request.out_dir))

    def refresh(self):
        job = self.manager.jobs.get(self.job_id)
        if not job:
            return
        r = job.request
        self.title.setText((job.title or r.url).upper())
        what = {Mode.BOTH: tr("mode_both"), Mode.VIDEO: tr("mode_video"), Mode.AUDIO: tr("mode_audio")}[r.mode]
        fmt = r.audio_format.upper() if r.mode is Mode.AUDIO else (f"{r.max_height}p" if r.max_height else tr("best"))
        parts = [job.service.upper(), what, fmt]
        if job.count > 1 or job.done_items > 1:
            parts.append(tr("items_progress", done=job.done_items, total=job.count or "?"))
        if job.item_title and job.item_title != job.title:
            parts.append(job.item_title)
        self.meta.setText(" // ".join(parts))
        st = job.state
        if st is State.QUEUED:
            text, ok = tr("st_queued"), True
        elif st is State.RUNNING:
            bits = [tr("st_running", p=int(job.progress * 100))]
            if job.speed:
                bits.append(_fmt_bytes(job.speed))
            if job.eta is not None:
                bits.append("ETA " + _fmt_eta(job.eta))
            text, ok = "  ·  ".join(bits), True
        elif st is State.PROCESSING:
            text, ok = tr("st_processing"), True
        elif st is State.DONE:
            text, ok = "✓ " + tr("st_done", n=job.done_items), True
        elif st is State.PARTIAL:
            text, ok = "◐ " + tr("st_partial", done=job.done_items, failed=job.failed_items), False
        elif st is State.CANCELLED:
            text, ok = "✕ " + tr("st_cancelled"), False
        else:
            text, ok = "✕ " + (job.error or tr("st_error")), False
        self.status.setText(text.upper() if st is not State.ERROR else text)
        self.status.setObjectName("ok" if ok else "bad")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        running = st in (State.RUNNING, State.PROCESSING)
        self.bar.setVisible(running)
        self.bar.setValue(int(job.progress * 1000))
        self.bar.setRange(0, 0 if st is State.PROCESSING else 1000)
        finished = st in FINISHED
        self.cancel.setVisible(not finished)
        self.retry.setVisible(st in (State.ERROR, State.PARTIAL, State.CANCELLED))
        self.remove.setVisible(finished)
        self.open.setVisible(st in (State.DONE, State.PARTIAL))
        self.setProperty("failed", st in (State.ERROR, State.PARTIAL))
        self.setProperty("done", st is State.DONE)
        self.style().unpolish(self)
        self.style().polish(self)


class QueuePage(QWidget):
    count_changed = Signal(int, int)

    def __init__(self, manager: DownloadManager):
        super().__init__()
        self.m = manager
        self.cards: dict[int, JobCard] = {}
        self.counter = 0
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 20, 28, 10)
        top = QHBoxLayout()
        self.summary = label("", "headline")
        top.addWidget(self.summary)
        top.addStretch()
        clean = _btn(tr("clear_finished"))
        clean.clicked.connect(self.clear_finished)
        top.addWidget(clean)
        v.addLayout(top)
        v.addSpacing(8)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.list_host = QWidget()
        self.list = QVBoxLayout(self.list_host)
        self.list.setContentsMargins(0, 0, 8, 0)
        self.list.setSpacing(10)
        self.empty = label(tr("queue_empty"), "muted")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list.addWidget(self.empty)
        self.list.addStretch()
        scroll.setWidget(self.list_host)
        v.addWidget(scroll, 1)
        manager.job_added.connect(self._added)
        manager.job_changed.connect(self._changed)
        self._update_summary()

    def _added(self, job_id: int):
        self.counter += 1
        card = JobCard(self.m.jobs[job_id], self.m, self.counter)
        card.retry.clicked.connect(lambda _=False, j=job_id: self._retry(j))
        card.remove.clicked.connect(lambda _=False, j=job_id: self._remove(j))
        self.cards[job_id] = card
        self.list.insertWidget(0, card)
        self._update_summary()

    def _changed(self, job_id: int):
        if card := self.cards.get(job_id):
            card.refresh()
        self._update_summary()

    def _retry(self, job_id: int):
        if self.m.retry(job_id):
            self._remove(job_id)

    def _remove(self, job_id: int):
        self.m.remove(job_id)
        if card := self.cards.pop(job_id, None):
            card.deleteLater()
        self._update_summary()

    def clear_finished(self):
        for jid in [j for j, job in self.m.jobs.items() if job.state in FINISHED]:
            self._remove(jid)

    def _update_summary(self):
        active = self.m.active()
        total = len(self.m.jobs)
        self.empty.setVisible(total == 0)
        self.summary.setText(tr("queue_summary", active=active, total=total).upper())
        self.count_changed.emit(active, total)


# ---------------------------------------------------------------- SERVIZI

class ServicesPage(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        v = QVBoxLayout(body)
        v.setContentsMargins(28, 20, 28, 28)
        v.addWidget(label(tr("services_title", n=len(SERVICES)).upper(), "headline"))
        intro = label(tr("services_intro"), "muted")
        intro.setWordWrap(True)
        v.addWidget(intro)
        v.addSpacing(10)
        grid = QGridLayout()
        grid.setSpacing(10)
        cols = 3
        for i, s in enumerate(SERVICES):
            card = QFrame()
            card.setObjectName("service")
            c = QVBoxLayout(card)
            c.setContentsMargins(12, 10, 12, 10)
            c.setSpacing(2)
            head = QHBoxLayout()
            head.addWidget(label(f"{i + 1:03d}", "index"))
            head.addSpacing(6)
            head.addWidget(label(s.name.upper(), "title"), 1)
            c.addLayout(head)
            kind = {"video": tr("kind_video"), "audio": tr("kind_audio"), "video+audio": tr("kind_both")}[s.kind]
            c.addWidget(label(f"{kind} // {s.domains[0]}", "meta"))
            lists = label("▤ " + s.lists, "muted")
            lists.setWordWrap(True)
            c.addWidget(lists)
            grid.addWidget(card, i // cols, i % cols)
        v.addLayout(grid)
        v.addSpacing(14)
        more = _btn("↗ " + tr("services_more"))
        more.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(SUPPORTED_URL)))
        v.addWidget(more, 0, Qt.AlignmentFlag.AlignLeft)
        v.addStretch()


# ---------------------------------------------------------------- SETUP

class _Task(QRunnable):
    class _S(QObject):
        done = Signal(object, object)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.signals = self._S()

    def run(self):
        try:
            self.signals.done.emit(self.fn(), None)
        except Exception as e:  # rete, PyPI, permessi: va tutto mostrato all'utente
            self.signals.done.emit(None, e)


class SetupPage(QWidget):
    concurrency_changed = Signal(int)

    def __init__(self, settings: Settings, manager: DownloadManager):
        super().__init__()
        self.s = settings
        self.m = manager
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)
        body = QWidget()
        scroll.setWidget(body)
        v = QVBoxLayout(body)
        v.setContentsMargins(28, 20, 28, 28)
        v.setSpacing(8)

        v.addWidget(label(tr("engine").upper(), "headline"))
        self.engine_info = label("", "meta")
        v.addWidget(self.engine_info)
        row = QHBoxLayout()
        self.update_btn = PunkButton(tr("update_engine"))
        self.update_btn.clicked.connect(self._update_engine)
        row.addWidget(self.update_btn)
        row.addSpacing(14)
        self.update_status = label("", "muted")
        self.update_status.setWordWrap(True)
        row.addWidget(self.update_status, 1)
        v.addLayout(row)
        self._refresh_engine()

        v.addSpacing(16)
        v.addWidget(label(tr("downloads").upper(), "headline"))
        g = QGridLayout()
        g.setHorizontalSpacing(16)
        g.setVerticalSpacing(6)
        g.addWidget(label(tr("parallel")), 0, 0)
        self.parallel = QSpinBox()
        self.parallel.setRange(1, 6)
        self.parallel.setValue(settings.get("parallel", 2, int))
        self.parallel.valueChanged.connect(self._parallel)
        g.addWidget(self.parallel, 1, 0)
        g.addWidget(label(tr("rate_limit")), 0, 1)
        self.rate = QLineEdit(settings.get("rate_limit", ""))
        self.rate.setPlaceholderText(tr("rate_placeholder"))
        self.rate.textChanged.connect(lambda t: settings.set("rate_limit", t))
        g.addWidget(self.rate, 1, 1)
        g.setColumnMinimumWidth(0, 140)
        g.setColumnMinimumWidth(1, 280)
        g.setColumnStretch(2, 1)
        v.addLayout(g)

        v.addSpacing(16)
        v.addWidget(label(tr("access").upper(), "headline"))
        info = label(tr("cookies_intro"), "muted")
        info.setWordWrap(True)
        v.addWidget(info)
        g2 = QGridLayout()
        g2.setHorizontalSpacing(16)
        g2.addWidget(label(tr("cookies_browser")), 0, 0)
        self.browser = _combo([(b.capitalize() if b else tr("none"), b) for b in BROWSERS], settings.get("cookies_browser", ""))
        self.browser.currentIndexChanged.connect(lambda: settings.set("cookies_browser", self.browser.currentData()))
        self.browser.setMinimumWidth(180)
        g2.addWidget(self.browser, 1, 0)
        g2.addWidget(label(tr("cookies_file")), 0, 1)
        cf = QHBoxLayout()
        self.cookie_file = QLineEdit(settings.get("cookies_file", ""))
        self.cookie_file.setPlaceholderText("cookies.txt")
        self.cookie_file.textChanged.connect(lambda t: settings.set("cookies_file", t.strip()))
        pick = _btn(tr("browse"))
        pick.clicked.connect(self._pick_cookies)
        cf.addWidget(self.cookie_file, 1)
        cf.addSpacing(8)
        cf.addWidget(pick)
        g2.addLayout(cf, 1, 1)
        g2.setColumnStretch(1, 1)
        v.addLayout(g2)

        v.addSpacing(16)
        v.addWidget(label(tr("language").upper(), "headline"))
        self.lang = _combo([(name, code) for code, name in LANGUAGES.items()], settings.get("language", ""))
        self.lang.insertItem(0, tr("system_language"), "")
        if not settings.get("language", ""):
            self.lang.setCurrentIndex(0)
        self.lang.currentIndexChanged.connect(self._language)
        self.lang.setMaximumWidth(320)
        v.addWidget(self.lang)

        v.addSpacing(20)
        v.addWidget(_rule())
        v.addSpacing(8)
        about = label(tr("about", v=__version__), "muted")
        about.setWordWrap(True)
        v.addWidget(about)
        for text, url in ((REPO_URL.removeprefix("https://"), REPO_URL),
                          ("github.com/yt-dlp/yt-dlp", "https://github.com/yt-dlp/yt-dlp"),
                          ("ffmpeg.org", "https://ffmpeg.org")):
            b = _btn("↗ " + text)
            b.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
            v.addWidget(b, 0, Qt.AlignmentFlag.AlignLeft)
        v.addStretch()

    def _refresh_engine(self):
        ff = tr("ffmpeg_ok") if self.m.ffmpeg else tr("ffmpeg_missing")
        self.engine_info.setText(f"yt-dlp {engine_update.installed_version()}  //  {ff}")

    def _update_engine(self):
        self.update_btn.setEnabled(False)
        self.update_status.setText(tr("updating"))
        task = _Task(engine_update.update)
        task.signals.done.connect(self._updated)
        QThreadPool.globalInstance().start(task)
        self._task = task

    def _updated(self, version, error):
        self.update_btn.setEnabled(True)
        if error:
            self.update_status.setText("✕ " + str(error))
        elif version is None:
            self.update_status.setText("✓ " + tr("up_to_date"))
        else:
            self.update_status.setText("✓ " + tr("updated", v=version))

    def _parallel(self, n: int):
        self.s.set("parallel", n)
        self.m.set_concurrency(n)

    def _pick_cookies(self):
        f, _ = QFileDialog.getOpenFileName(self, "cookies.txt", str(Path.home()), "cookies (*.txt);;* (*)")
        if f:
            self.cookie_file.setText(f)

    def _language(self):
        code = self.lang.currentData()
        self.s.set("language", code)
        QMessageBox.information(self, "Freedom", tr("restart_needed", lang=code or "auto"))


# ---------------------------------------------------------------- FINESTRA

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.s = Settings()
        set_language(self.s.get("language", ""))
        self.manager = DownloadManager(self.s.get("parallel", 2, int))
        self.setWindowTitle("Freedom")
        self.resize(1100, 780)
        self.setMinimumSize(860, 620)
        self.setAcceptDrops(True)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(28, 20, 28, 14)
        header.addWidget(Mark(60))
        header.addSpacing(14)
        titles = QVBoxLayout()
        titles.setSpacing(0)
        titles.addWidget(label("FREEDOM", "display"))
        titles.addWidget(label(tr("tagline"), "muted"))
        header.addLayout(titles)
        header.addStretch()
        stamp = label(tr("stamp", n=len(SERVICES)), "stamp")
        header.addWidget(stamp, 0, Qt.AlignmentFlag.AlignTop)
        v.addLayout(header)
        v.addWidget(_rule())

        tabs = QHBoxLayout()
        tabs.setSpacing(0)
        tabs.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.download_page = DownloadPage(self.s)
        self.queue_page = QueuePage(self.manager)
        self.setup_page = SetupPage(self.s, self.manager)
        pages = ((tr("tab_download"), self.download_page), (tr("tab_queue"), self.queue_page),
                 (tr("tab_services"), ServicesPage()), (tr("tab_setup"), self.setup_page))
        self.tab_group = QButtonGroup(self)
        self.tab_buttons: list[QPushButton] = []
        self.tab_labels: list[str] = []
        for i, (text, page) in enumerate(pages):
            b = _btn(text.upper(), "tab")
            b.setCheckable(True)
            self.tab_group.addButton(b, i)
            self.tab_buttons.append(b)
            self.tab_labels.append(text.upper())
            tabs.addWidget(b, 1)
            self.stack.addWidget(page)
        self.tab_group.idClicked.connect(self.show_tab)
        v.addLayout(tabs)
        v.addWidget(_rule())
        v.addWidget(self.stack, 1)

        self.download_page.submitted.connect(self._submit)
        self.queue_page.count_changed.connect(self._counts)
        self.show_tab(0)

        # Il link copiato mentre la finestra è aperta finisce nel box: comodo per le compilation.
        self._last_clip = QGuiApplication.clipboard().text()
        self._clip_timer = QTimer(self, interval=1200, timeout=self._watch_clipboard)
        self._clip_timer.start()

    def show_tab(self, i: int):
        self.stack.setCurrentIndex(i)
        for j, b in enumerate(self.tab_buttons):
            b.setChecked(j == i)
            b.setText(f"[{self.tab_labels[j]}]" if j == i else self.tab_labels[j])

    def _submit(self, reqs: list[Request]):
        for r in reqs:
            self.manager.submit(r)
        self.show_tab(1)

    def _counts(self, active: int, total: int):
        base = tr("tab_queue").upper()
        self.tab_labels[1] = f"{base} ({active})" if active else base
        self.show_tab(self.stack.currentIndex())
        self.setWindowTitle(f"Freedom — {tr('queue_summary', active=active, total=total)}" if active else "Freedom")

    def _watch_clipboard(self):
        text = QGuiApplication.clipboard().text()
        if text == self._last_clip:
            return
        self._last_clip = text
        if self.isActiveWindow():
            return
        urls = [u for u in split_urls(text) if detect(u)]
        if urls and self.s.get("watch_clipboard", True, bool):
            existing = set(split_urls(self.download_page.urls.toPlainText()))
            new = [u for u in urls if u not in existing]
            if new:
                self.download_page.add_urls("\n".join(new))

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() or e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e):
        md = e.mimeData()
        text = "\n".join(u.toString() for u in md.urls()) if md.hasUrls() else md.text()
        if split_urls(text):
            self.download_page.add_urls(text)
            self.show_tab(0)

    def closeEvent(self, e):
        if self.manager.active():
            answer = QMessageBox.question(self, "Freedom", tr("quit_active", n=self.manager.active()))
            if answer != QMessageBox.StandardButton.Yes:
                e.ignore()
                return
            for jid in list(self.manager.jobs):
                self.manager.cancel(jid)
            self.manager.pool.waitForDone(5000)
        e.accept()
