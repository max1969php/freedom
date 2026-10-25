from freedom.sites import SERVICES, detect, split_urls


def test_at_least_twenty_services():
    assert len(SERVICES) >= 20


def test_detect_prefers_most_specific_domain():
    assert detect("https://music.youtube.com/playlist?list=x").name == "YouTube Music"
    assert detect("https://www.youtube.com/watch?v=x").name == "YouTube"
    assert detect("https://m.youtube.com/watch?v=x").name == "YouTube"
    assert detect("https://artist.bandcamp.com/album/y").name == "Bandcamp"
    assert detect("https://raiplaysound.it/x").name == "RaiPlay Sound"
    assert detect("https://notyoutube.com/x") is None


def test_split_urls_dedupes_and_fixes_scheme():
    text = "https://youtu.be/a, https://youtu.be/a\n soundcloud.com/u/t  junk"
    assert split_urls(text) == ["https://youtu.be/a", "https://soundcloud.com/u/t"]


def test_yt_dlp_has_an_extractor_for_every_service():
    from yt_dlp.extractor import gen_extractor_classes

    extractors = [e for e in gen_extractor_classes() if e.IE_NAME != "generic"]
    samples = {
        "YouTube": "https://www.youtube.com/watch?v=BaW_jenozKc",
        "YouTube Music": "https://music.youtube.com/watch?v=BaW_jenozKc",
        "Vimeo": "https://vimeo.com/56015672",
        "Dailymotion": "https://www.dailymotion.com/video/x5kesuj",
        "Twitch": "https://www.twitch.tv/videos/6528877",
        "TikTok": "https://www.tiktok.com/@leenabhushan/video/6748451240264420610",
        "Instagram": "https://www.instagram.com/p/aye83DjauH/",
        "Facebook": "https://www.facebook.com/watch/?v=274175099429670",
        "X / Twitter": "https://x.com/freethenipple/status/643211948184596480",
        "Reddit": "https://www.reddit.com/r/videos/comments/6rrwyj/that_small_heart_attack/",
        "SoundCloud": "https://soundcloud.com/ethmusic/lostin-powers-she-so-heavy",
        "Bandcamp": "https://youtube-dl.bandcamp.com/track/youtube-dl-test-song",
        "Mixcloud": "https://www.mixcloud.com/dholbach/cryptkeeper/",
        "Audiomack": "https://audiomack.com/song/roosh-williams/extraordinary",
        "Internet Archive": "https://archive.org/details/XD300-23_68HighlightsAResearchCntAugHumanIntellect",
        "Bilibili": "https://www.bilibili.com/video/BV13x41117TL",
        "Niconico": "https://www.nicovideo.jp/watch/sm22312215",
        "Rumble": "https://rumble.com/v5pv5f8-the-golden-age-of-tv.html",
        "Odysee": "https://odysee.com/@BrodieRobertson:5/apple-is-tracking-everything-you-do-on:e",
        "PeerTube": "https://framatube.org/videos/watch/9c9de5e8-0a1e-484a-b099-e80766180a6d",
        "Bitchute": "https://www.bitchute.com/video/UGlrF9o9b-Q/",
        "Streamable": "https://streamable.com/dnd1",
        "TED": "https://www.ted.com/talks/dan_dennett_on_our_consciousness",
        "RaiPlay": "https://www.raiplay.it/video/2014/04/Report-del-07042014-cb27157f-9dd0-4aee-b788-b1f67643a391.html",
        "RaiPlay Sound": "https://www.raiplaysound.it/audio/2021/12/IL-RUGGITO-DEL-CONIGLIO-1ebae2a7-7cdb-42bb-842e-fe0d193e9707.html",
        "ARTE": "https://www.arte.tv/fr/videos/088501-000-A/mexico-stealing-petrol-to-survive/",
        "Spreaker": "https://www.spreaker.com/episode/12534508",
        "Kick": "https://kick.com/xqc/videos/58bac65b-e641-4476-a7ba-3707a35e60e3",
    }
    assert set(samples) == {s.name for s in SERVICES}
    missing = [name for name, url in samples.items() if not any(e.suitable(url) for e in extractors)]
    assert not missing, missing
