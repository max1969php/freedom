from __future__ import annotations

import itertools
import os
import shutil
import sys
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

import yt_dlp
from yt_dlp.utils import DownloadCancelled

from .options import Request, build_ydl_opts
from .sites import detect


class State(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PROCESSING = "processing"
    DONE = "done"
    PARTIAL = "partial"
    ERROR = "error"
    CANCELLED = "cancelled"


FINISHED = {State.DONE, State.PARTIAL, State.ERROR, State.CANCELLED}


@dataclass
class Job:
    id: int
    request: Request
    service: str
    state: State = State.QUEUED
    title: str = ""
    progress: float = 0.0
    speed: float | None = None
    eta: int | None = None
    index: int = 0
    count: int = 0
    done_items: int = 0
    failed_items: int = 0
    last_file: str = ""
    item_title: str = ""
    error: str = ""
    cancel: threading.Event = field(default_factory=threading.Event, repr=False)


def _bundled(name: str) -> Path | None:
    """Un eseguibile incluso nel pacchetto (accanto all'exe congelato, o in desktop/vendor in sviluppo)."""
    exe = name + ".exe" if sys.platform == "win32" else name
    roots = []
    if getattr(sys, "frozen", False):
        roots.append(Path(sys.executable).parent)
        roots.append(Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)))
    roots.append(Path(__file__).resolve().parent.parent / "vendor")
    for root in roots:
        p = root / exe
        if p.is_file():
            return p
    return None


def find_ffmpeg() -> str | None:
    """L'ffmpeg incluso nell'installer (Windows) vince su quello di sistema."""
    if p := _bundled("ffmpeg"):
        return str(p.parent)
    found = shutil.which("ffmpeg")
    return str(Path(found).parent) if found else None


def js_runtimes() -> dict:
    """YouTube vuole un runtime JS per i formati migliori: Deno incluso, poi quelli già sul sistema."""
    deno = _bundled("deno")
    return {"deno": {"path": str(deno)} if deno else {}, "node": {}, "bun": {}, "quickjs": {}}


class _Logger:
    def __init__(self, sink):
        self.sink = sink

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.sink(msg)


class _Signals(QObject):
    update = Signal(int, dict)


class _Worker(QRunnable):
    def __init__(self, job: Job, signals: _Signals):
        super().__init__()
        self.job = job
        self.signals = signals
        self.errors: list[str] = []
        self._seen: set[str] = set()

    def emit(self, **changes):
        self.signals.update.emit(self.job.id, changes)

    def _progress(self, d: dict):
        if self.job.cancel.is_set():
            raise DownloadCancelled()
        info = d.get("info_dict") or {}
        changes: dict = {"state": State.RUNNING}
        if info.get("title"):
            changes["title"] = info.get("playlist_title") or info["title"]
            changes["item_title"] = info["title"]
        if info.get("playlist_index"):
            changes["index"] = int(info["playlist_index"])
            changes["count"] = int(info.get("n_entries") or info.get("playlist_count") or 0)
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                changes["progress"] = min(1.0, d.get("downloaded_bytes", 0) / total)
            elif d.get("fragment_count"):
                changes["progress"] = min(1.0, (d.get("fragment_index") or 0) / d["fragment_count"])
            changes["speed"] = d.get("speed")
            changes["eta"] = d.get("eta")
        elif d["status"] == "finished":
            changes.update(progress=1.0, speed=None, eta=None, state=State.PROCESSING)
        self.emit(**changes)

    def _postprocess(self, d: dict):
        if self.job.cancel.is_set():
            raise DownloadCancelled()
        if d["status"] == "finished" and d.get("postprocessor") == "MoveFiles":
            info = d.get("info_dict") or {}
            path = info.get("filepath") or info.get("_filename") or ""
            key = info.get("id") or path
            if key not in self._seen:
                self._seen.add(key)
                self.emit(done_items=len(self._seen), last_file=path, state=State.RUNNING, progress=0.0)

    @Slot()
    def run(self):
        req = self.job.request
        opts = build_ydl_opts(req)
        opts["progress_hooks"] = [self._progress]
        opts["postprocessor_hooks"] = [self._postprocess]
        opts["logger"] = _Logger(self.errors.append)
        if self.job.cancel.is_set():
            self.emit(state=State.CANCELLED)
            return
        self.emit(state=State.RUNNING)
        try:
            Path(req.out_dir).mkdir(parents=True, exist_ok=True)
            with yt_dlp.YoutubeDL(opts) as ydl:
                code = ydl.download([req.url])
        except DownloadCancelled:
            self.emit(state=State.CANCELLED, speed=None, eta=None)
            return
        except Exception as e:  # yt-dlp solleva molte eccezioni diverse: tutte finiscono nella scheda
            self.emit(state=State.ERROR, error=_clean(str(e)) or _clean(self.errors[-1] if self.errors else ""))
            return
        done = len(self._seen)
        failed = len(self.errors)
        if self.job.cancel.is_set():
            state = State.CANCELLED
        elif not done:
            state = State.ERROR
        elif failed or code:
            state = State.PARTIAL
        else:
            state = State.DONE
        self.emit(
            state=state, progress=1.0 if done else 0.0, speed=None, eta=None, done_items=done, failed_items=failed,
            error=_clean(self.errors[-1]) if self.errors else "",
        )


def _clean(msg: str) -> str:
    msg = msg.strip()
    for prefix in ("ERROR:", "\x1b[0;31mERROR:\x1b[0m"):
        msg = msg.removeprefix(prefix).strip()
    return msg.splitlines()[0] if msg else ""


class DownloadManager(QObject):
    job_added = Signal(int)
    job_changed = Signal(int)

    def __init__(self, concurrency: int = 2):
        super().__init__()
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(concurrency)
        self.jobs: dict[int, Job] = {}
        self._ids = itertools.count(1)
        self._signals = _Signals()
        self._signals.update.connect(self._apply)
        self.ffmpeg = find_ffmpeg()
        self.js_runtimes = js_runtimes()

    def set_concurrency(self, n: int):
        self.pool.setMaxThreadCount(max(1, n))

    def submit(self, req: Request) -> Job:
        if req.ffmpeg_location is None:
            req.ffmpeg_location = self.ffmpeg
        if req.js_runtimes is None:
            req.js_runtimes = self.js_runtimes
        service = detect(req.url)
        job = Job(id=next(self._ids), request=req, service=service.name if service else _host(req.url))
        self.jobs[job.id] = job
        self.job_added.emit(job.id)
        self.pool.start(_Worker(job, self._signals))
        return job

    def cancel(self, job_id: int):
        job = self.jobs.get(job_id)
        if not job or job.state in FINISHED:
            return
        job.cancel.set()
        self.job_changed.emit(job_id)

    def retry(self, job_id: int) -> Job | None:
        job = self.jobs.get(job_id)
        if not job or job.state not in FINISHED:
            return None
        return self.submit(job.request)

    def remove(self, job_id: int):
        job = self.jobs.get(job_id)
        if job and job.state in FINISHED:
            del self.jobs[job_id]

    def active(self) -> int:
        return sum(1 for j in self.jobs.values() if j.state not in FINISHED)

    @Slot(int, dict)
    def _apply(self, job_id: int, changes: dict):
        job = self.jobs.get(job_id)
        if not job:
            return
        # Il passaggio per il segnale Qt trasforma l'enum in str semplice.
        if "state" in changes:
            changes["state"] = State(changes["state"])
        for k, v in changes.items():
            setattr(job, k, v)
        self.job_changed.emit(job_id)


def _host(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).hostname or "?").removeprefix("www.")


def open_path(path: str):
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606
    else:
        import subprocess

        subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
