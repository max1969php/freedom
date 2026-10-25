from freedom.options import Mode, Request, build_ydl_opts, format_selector, parse_rate


def req(**kw):
    return Request(url="https://example.com/v", out_dir="/tmp/x", **kw)


def keys(opts):
    return [p["key"] for p in opts["postprocessors"]]


def test_both_mp4_prefers_native_streams_and_merges():
    opts = build_ydl_opts(req(max_height=1080))
    assert opts["format"].startswith("bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]")
    assert opts["merge_output_format"] == "mp4"
    assert "EmbedThumbnail" in keys(opts) and opts["writethumbnail"]


def test_audio_mode_extracts_with_bitrate():
    opts = build_ydl_opts(req(mode=Mode.AUDIO, audio_format="mp3", audio_bitrate="192"))
    assert opts["format"] == "bestaudio/best"
    pp = opts["postprocessors"][0]
    assert pp == {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
    assert "merge_output_format" not in opts


def test_lossless_audio_ignores_bitrate_and_wav_has_no_cover():
    opts = build_ydl_opts(req(mode=Mode.AUDIO, audio_format="wav"))
    assert opts["postprocessors"][0]["preferredquality"] == "0"
    assert "EmbedThumbnail" not in keys(opts) and not opts["writethumbnail"]


def test_video_only_has_no_audio_and_no_cover():
    opts = build_ydl_opts(req(mode=Mode.VIDEO, max_height=720))
    assert format_selector(req(mode=Mode.VIDEO, max_height=720)).startswith("bestvideo[height<=720]")
    assert "EmbedThumbnail" not in keys(opts)


def test_webm_container_skips_thumbnail_and_remuxes():
    opts = build_ydl_opts(req(container="webm"))
    assert "FFmpegVideoRemuxer" in keys(opts)
    assert "EmbedThumbnail" not in keys(opts)


def test_single_vs_compilation():
    single = build_ydl_opts(req(playlist=False))
    assert single["noplaylist"] is True and "playlist" not in single["outtmpl"]["default"]
    comp = build_ydl_opts(req(playlist=True, playlist_items=" 1-5,9 "))
    assert comp["noplaylist"] is False
    assert comp["playlist_items"] == "1-5,9"
    assert comp["ignoreerrors"] == "only_download"
    assert comp["outtmpl"]["pl_thumbnail"] == ""


def test_playlist_items_go_in_a_numbered_subfolder_and_singles_stay_on_top():
    import yt_dlp

    y = yt_dlp.YoutubeDL({**build_ydl_opts(req(playlist=True)), "paths": {"home": "/out"}})
    in_list = dict(id="a", title="Song: x/y", ext="mp3", playlist_title="Best: of/all", playlist_index=7)
    assert y.prepare_filename(in_list) == "/out/Best： of⧸all/007 - Song： x⧸y [a].mp3"
    assert y.prepare_filename(dict(id="a", title="Song", ext="mp3")) == "/out/Song [a].mp3"


def test_cookies_file_wins_over_browser():
    assert build_ydl_opts(req(cookies_browser="firefox"))["cookiesfrombrowser"] == ("firefox",)
    opts = build_ydl_opts(req(cookies_browser="firefox", cookies_file="/c.txt"))
    assert opts["cookiefile"] == "/c.txt" and "cookiesfrombrowser" not in opts


def test_parse_rate():
    assert parse_rate("2M") == 2 * 1024**2
    assert parse_rate("500k") == 500 * 1024
    assert parse_rate("1.5MB/s") == int(1.5 * 1024**2)
    assert parse_rate("") is None
    assert parse_rate("abc") is None


def test_opts_are_accepted_by_yt_dlp():
    import yt_dlp

    for mode in Mode:
        with yt_dlp.YoutubeDL(build_ydl_opts(req(mode=mode, subtitles=True))):
            pass


def test_js_runtimes_are_accepted_by_yt_dlp():
    import yt_dlp

    from freedom.engine import js_runtimes

    opts = build_ydl_opts(req(js_runtimes=js_runtimes()))
    assert list(opts["js_runtimes"])[0] == "deno"
    with yt_dlp.YoutubeDL(opts):
        pass
