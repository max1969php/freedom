from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Service:
    name: str
    domains: tuple[str, ...]
    kind: str  # "video", "audio", "video+audio"
    lists: str  # cosa scarica "a compilation"


SERVICES: tuple[Service, ...] = (
    Service("YouTube", ("youtube.com", "youtu.be"), "video+audio", "playlist, canali, Shorts"),
    Service("YouTube Music", ("music.youtube.com",), "audio", "album, playlist"),
    Service("Vimeo", ("vimeo.com",), "video", "album, canali, showcase"),
    Service("Dailymotion", ("dailymotion.com", "dai.ly"), "video", "playlist, utenti"),
    Service("Twitch", ("twitch.tv",), "video", "VOD, clip, collezioni"),
    Service("TikTok", ("tiktok.com",), "video", "profili, hashtag"),
    Service("Instagram", ("instagram.com",), "video", "post multipli, reel"),
    Service("Facebook", ("facebook.com", "fb.watch"), "video", "video, reel"),
    Service("X / Twitter", ("x.com", "twitter.com"), "video", "thread con più video"),
    Service("Reddit", ("reddit.com", "redd.it"), "video", "post"),
    Service("SoundCloud", ("soundcloud.com",), "audio", "set, profili, like"),
    Service("Bandcamp", ("bandcamp.com",), "audio", "album, discografie"),
    Service("Mixcloud", ("mixcloud.com",), "audio", "profili, playlist"),
    Service("Audiomack", ("audiomack.com",), "audio", "album, playlist"),
    Service("Internet Archive", ("archive.org",), "video+audio", "collezioni"),
    Service("Bilibili", ("bilibili.com", "b23.tv"), "video", "serie, playlist"),
    Service("Niconico", ("nicovideo.jp",), "video", "mylist, serie"),
    Service("Rumble", ("rumble.com",), "video", "canali"),
    Service("Odysee", ("odysee.com",), "video", "canali, playlist"),
    Service("PeerTube", ("framatube.org", "peertube.tv", "tilvids.com"), "video", "canali, playlist"),
    Service("Bitchute", ("bitchute.com",), "video", "canali"),
    Service("Streamable", ("streamable.com",), "video", "singoli"),
    Service("TED", ("ted.com",), "video", "playlist"),
    Service("RaiPlay", ("raiplay.it",), "video", "programmi"),
    Service("RaiPlay Sound", ("raiplaysound.it",), "audio", "podcast, programmi"),
    Service("ARTE", ("arte.tv",), "video", "collezioni"),
    Service("Spreaker", ("spreaker.com",), "audio", "podcast"),
    Service("Kick", ("kick.com",), "video", "VOD, clip"),
)


def detect(url: str) -> Service | None:
    host = (urlparse(url.strip()).hostname or "").lower().removeprefix("www.").removeprefix("m.")
    best: Service | None = None
    best_len = -1
    for s in SERVICES:
        for d in s.domains:
            if (host == d or host.endswith("." + d)) and len(d) > best_len:
                best, best_len = s, len(d)
    return best


def split_urls(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for token in text.replace(",", " ").split():
        token = token.strip().strip("<>\"'")
        if token.startswith(("http://", "https://")):
            seen.setdefault(token)
        elif "." in token and "/" in token and " " not in token:
            seen.setdefault("https://" + token)
    return list(seen)
