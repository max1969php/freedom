from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    BOTH = "both"
    VIDEO = "video"
    AUDIO = "audio"


AUDIO_FORMATS = ("mp3", "m4a", "opus", "flac", "wav", "best")
VIDEO_CONTAINERS = ("mp4", "mkv", "webm")
QUALITIES = (0, 2160, 1440, 1080, 720, 480, 360)  # 0 = la migliore disponibile
AUDIO_BITRATES = ("320", "256", "192", "128")
BROWSERS = ("", "firefox", "chrome", "chromium", "edge", "brave", "opera", "vivaldi", "safari")


@dataclass
class Request:
    url: str
    out_dir: str
    mode: Mode = Mode.BOTH
    max_height: int = 0
    container: str = "mp4"
    audio_format: str = "mp3"
    audio_bitrate: str = "320"
    playlist: bool = True
    playlist_items: str = ""
    subtitles: bool = False
    embed_thumbnail: bool = True
    embed_metadata: bool = True
    cookies_browser: str = ""
    cookies_file: str = ""
    rate_limit: str = ""
    ffmpeg_location: str | None = None
    js_runtimes: dict | None = None
    extra: dict = field(default_factory=dict)


def format_selector(req: Request) -> str:
    h = f"[height<={req.max_height}]" if req.max_height else ""
    if req.mode is Mode.AUDIO:
        return "bestaudio/best"
    if req.mode is Mode.VIDEO:
        return f"bestvideo{h}/best{h}[acodec=none]/bestvideo/best{h}/best"
    if req.container == "mp4":
        # mp4 nativo quando c'è (niente ricodifica), altrimenti ffmpeg unisce in mp4 il meglio.
        return (
            f"bestvideo{h}[ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo{h}+bestaudio/best{h}/best"
        )
    return f"bestvideo{h}+bestaudio/best{h}/best"


SINGLE_TEMPLATE = "%(title).180B [%(id)s].%(ext)s"
# Le voci di una playlist vanno in una sottocartella col suo nome, numerate; un link singolo resta in
# cima ("." quando non c'è playlist). Lo "/" deve stare fuori dai campi: dentro verrebbe sanificato.
PLAYLIST_TEMPLATE = (
    "%(playlist_title,playlist_id&{:.100}|.)s/%(playlist_index&{:03d} - |)s%(title).160B [%(id)s].%(ext)s"
)


def output_template(req: Request) -> dict:
    # pl_thumbnail vuoto: niente copertina della playlist lasciata in giro come .jpg.
    return {"default": PLAYLIST_TEMPLATE if req.playlist else SINGLE_TEMPLATE, "pl_thumbnail": ""}


def postprocessors(req: Request) -> list[dict]:
    pps: list[dict] = []
    if req.mode is Mode.AUDIO:
        pps.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": req.audio_format,
            "preferredquality": "0" if req.audio_format in ("flac", "wav", "best") else req.audio_bitrate,
        })
    elif req.mode is Mode.BOTH and req.container != "mp4":
        pps.append({"key": "FFmpegVideoRemuxer", "preferedformat": req.container})
    if req.subtitles and req.mode is not Mode.AUDIO:
        pps.append({"key": "FFmpegEmbedSubtitle", "already_have_subtitle": False})
    if req.embed_metadata:
        pps.append({"key": "FFmpegMetadata", "add_metadata": True, "add_chapters": req.mode is not Mode.AUDIO})
    # EmbedThumbnail fallisce sui contenitori che non la reggono (webm, wav, solo-video di estensione ignota).
    if req.mode is Mode.AUDIO:
        thumb_ok = req.audio_format in ("mp3", "m4a", "opus", "flac")
    else:
        thumb_ok = req.mode is Mode.BOTH and req.container in ("mp4", "mkv")
    if req.embed_thumbnail and thumb_ok:
        pps.append({"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"})
        pps.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
    return pps


def parse_rate(value: str) -> int | None:
    value = value.strip().upper().removesuffix("/S").removesuffix("B")
    if not value:
        return None
    mult = {"K": 1024, "M": 1024**2, "G": 1024**3}.get(value[-1], 1)
    number = value[:-1] if value[-1] in "KMG" else value
    try:
        return int(float(number) * mult)
    except ValueError:
        return None


def build_ydl_opts(req: Request) -> dict:
    opts: dict = {
        "format": format_selector(req),
        "paths": {"home": req.out_dir, "temp": req.out_dir},
        "outtmpl": output_template(req),
        "noplaylist": not req.playlist,
        "ignoreerrors": "only_download" if req.playlist else False,
        "postprocessors": postprocessors(req),
        "writethumbnail": any(p["key"] == "EmbedThumbnail" for p in postprocessors(req)),
        "windowsfilenames": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "noprogress": True,
        "quiet": True,
        "no_warnings": False,
        "updatetime": False,
    }
    if req.mode is Mode.BOTH:
        opts["merge_output_format"] = req.container
    if req.playlist and req.playlist_items.strip():
        opts["playlist_items"] = req.playlist_items.strip()
    if req.subtitles and req.mode is not Mode.AUDIO:
        opts.update(writesubtitles=True, subtitleslangs=["it", "en", "-live_chat"])
    if req.cookies_file:
        opts["cookiefile"] = req.cookies_file
    elif req.cookies_browser:
        opts["cookiesfrombrowser"] = (req.cookies_browser,)
    rate = parse_rate(req.rate_limit)
    if rate:
        opts["ratelimit"] = rate
    if req.ffmpeg_location:
        opts["ffmpeg_location"] = req.ffmpeg_location
    if req.js_runtimes:
        opts["js_runtimes"] = req.js_runtimes
    opts.update(req.extra)
    return opts
