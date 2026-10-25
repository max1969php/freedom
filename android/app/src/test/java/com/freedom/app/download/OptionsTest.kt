package com.freedom.app.download

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class OptionsTest {
    private fun args(r: Request) = Options.args(r, "/out", "/out/.done", null)
    private fun List<String>.after(flag: String) = this[indexOf(flag) + 1]

    @Test fun bothMp4PrefersNativeStreams() {
        val a = args(Request("u", maxHeight = 1080))
        assertTrue(a.after("-f").startsWith("bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]"))
        assertEquals("mp4", a.after("--merge-output-format"))
        assertTrue("--embed-thumbnail" in a)
    }

    @Test fun audioModeExtracts() {
        val a = args(Request("u", mode = Mode.AUDIO, audioFormat = "mp3", audioBitrate = "192"))
        assertEquals("bestaudio/best", a.after("-f"))
        assertTrue("-x" in a)
        assertEquals("192K", a.after("--audio-quality"))
        assertFalse("--merge-output-format" in a)
    }

    @Test fun losslessAndWav() {
        val a = args(Request("u", mode = Mode.AUDIO, audioFormat = "wav"))
        assertEquals("0", a.after("--audio-quality"))
        assertFalse("--embed-thumbnail" in a)
    }

    @Test fun singleVsCompilation() {
        assertTrue("--no-playlist" in args(Request("u", playlist = false)))
        val c = args(Request("u", playlist = true, playlistItems = " 1-5 "))
        assertTrue("--yes-playlist" in c && "--ignore-errors" in c)
        assertEquals("1-5", c.after("-I"))
        assertEquals(Options.PLAYLIST_TEMPLATE, c[c.indexOf("-o") + 1])
        assertTrue("pl_thumbnail:" in c)
        val s = args(Request("u", playlist = false))
        assertEquals(Options.SINGLE_TEMPLATE, s.after("-o"))
    }

    @Test fun cookiesAndDoneLog() {
        val a = Options.args(Request("u"), "/o", "/o/.done", "/c.txt")
        assertEquals("/c.txt", a.after("--cookies"))
        assertEquals("/o/.done", a[a.size - 1])
        assertEquals("after_move:filepath", a[a.size - 2])
    }

    @Test fun parser() {
        assertEquals(3 to 12, OutputParser.item("[download] Downloading item 3 of 12"))
        assertNull(OutputParser.item("[download]  42.0% of 3.00MiB"))
        assertEquals("Song", OutputParser.title("[download] Destination: /x/Album/003 - Song [abc].f140.m4a"))
        assertEquals("Clip", OutputParser.title("[Merger] Merging formats into \"/x/Clip [id].mp4\""))
        assertEquals("Video unavailable", OutputParser.error("foo\nERROR: Video unavailable\n"))
    }
}

class SitesTest {
    @Test fun atLeastTwenty() = assertTrue(Sites.SERVICES.size >= 20)

    @Test fun detect() {
        assertEquals("YouTube Music", Sites.detect("https://music.youtube.com/watch?v=x")?.name)
        assertEquals("YouTube", Sites.detect("https://m.youtube.com/watch?v=x")?.name)
        assertEquals("Bandcamp", Sites.detect("https://artist.bandcamp.com/album/y")?.name)
        assertNull(Sites.detect("https://notyoutube.com/x"))
    }

    @Test fun split() = assertEquals(
        listOf("https://youtu.be/a", "https://soundcloud.com/u/t"),
        Sites.splitUrls("https://youtu.be/a, https://youtu.be/a\n soundcloud.com/u/t junk"),
    )
}
