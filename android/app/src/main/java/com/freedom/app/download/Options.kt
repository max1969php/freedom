package com.freedom.app.download

enum class Mode { BOTH, VIDEO, AUDIO }

val AUDIO_FORMATS = listOf("mp3", "m4a", "opus", "flac", "wav", "best")
val VIDEO_CONTAINERS = listOf("mp4", "mkv", "webm")
val QUALITIES = listOf(0, 2160, 1440, 1080, 720, 480, 360)
val AUDIO_BITRATES = listOf("320", "256", "192", "128")

/** Cosa scaricare: la stessa struttura di freedom/options.py del desktop. */
data class Request(
    val url: String,
    val mode: Mode = Mode.BOTH,
    val maxHeight: Int = 0,
    val container: String = "mp4",
    val audioFormat: String = "mp3",
    val audioBitrate: String = "320",
    val playlist: Boolean = true,
    val playlistItems: String = "",
    val subtitles: Boolean = false,
    val embedThumbnail: Boolean = true,
    val embedMetadata: Boolean = true,
    val rateLimit: String = "",
)

object Options {
    const val SINGLE_TEMPLATE = "%(title).150B [%(id)s].%(ext)s"
    const val PLAYLIST_TEMPLATE =
        "%(playlist_title,playlist_id&{:.100}|.)s/%(playlist_index&{:03d} - |)s%(title).120B [%(id)s].%(ext)s"

    fun formatSelector(r: Request): String {
        val h = if (r.maxHeight > 0) "[height<=${r.maxHeight}]" else ""
        return when (r.mode) {
            Mode.AUDIO -> "bestaudio/best"
            Mode.VIDEO -> "bestvideo$h/best$h[acodec=none]/bestvideo/best$h/best"
            Mode.BOTH -> if (r.container == "mp4") {
                "bestvideo$h[ext=mp4]+bestaudio[ext=m4a]/bestvideo$h+bestaudio/best$h/best"
            } else {
                "bestvideo$h+bestaudio/best$h/best"
            }
        }
    }

    fun embedsThumbnail(r: Request): Boolean = r.embedThumbnail && when (r.mode) {
        Mode.AUDIO -> r.audioFormat in setOf("mp3", "m4a", "opus", "flac")
        Mode.BOTH -> r.container == "mp4" || r.container == "mkv"
        Mode.VIDEO -> false
    }

    /** Argomenti per yt-dlp; [outDir] è una cartella temporanea del job, [doneLog] riceve i file finiti. */
    fun args(r: Request, outDir: String, doneLog: String, cookies: String?): List<String> = buildList {
        add("-f"); add(formatSelector(r))
        add("-P"); add(outDir)
        // Come desktop/freedom/options.py: voci di playlist in una sottocartella numerata, singoli in cima.
        add("-o"); add(if (r.playlist) PLAYLIST_TEMPLATE else SINGLE_TEMPLATE)
        add("-o"); add("pl_thumbnail:")
        if (r.playlist) {
            add("--yes-playlist")
            add("--ignore-errors")
            if (r.playlistItems.isNotBlank()) { add("-I"); add(r.playlistItems.trim()) }
        } else {
            add("--no-playlist")
        }
        when (r.mode) {
            Mode.AUDIO -> {
                add("-x")
                add("--audio-format"); add(r.audioFormat)
                add("--audio-quality"); add(if (r.audioFormat in setOf("flac", "wav", "best")) "0" else "${r.audioBitrate}K")
            }
            Mode.BOTH -> {
                add("--merge-output-format"); add(r.container)
                if (r.container != "mp4") { add("--remux-video"); add(r.container) }
            }
            Mode.VIDEO -> Unit
        }
        if (r.subtitles && r.mode != Mode.AUDIO) {
            add("--write-subs"); add("--sub-langs"); add("it,en,-live_chat"); add("--embed-subs")
        }
        if (r.embedMetadata) {
            add("--embed-metadata")
            if (r.mode != Mode.AUDIO) add("--embed-chapters")
        }
        if (embedsThumbnail(r)) {
            add("--embed-thumbnail"); add("--convert-thumbnails"); add("jpg")
        }
        if (r.rateLimit.isNotBlank()) { add("-r"); add(r.rateLimit.trim()) }
        if (cookies != null) { add("--cookies"); add(cookies) }
        add("--windows-filenames")
        add("--no-mtime")
        add("-N"); add("4")
        add("--retries"); add("10")
        add("--fragment-retries"); add("10")
        add("--newline")
        add("--print-to-file"); add("after_move:filepath"); add(doneLog)
    }
}

/** Righe di yt-dlp che interessano la scheda: voce corrente di una compilation e titolo. */
object OutputParser {
    private val item = Regex("""\[download] Downloading (?:item|video) (\d+) of (\d+)""")
    private val dest = Regex("""\[(?:download|Merger|ExtractAudio)] (?:Destination: |Merging formats into ")(.+?)"?$""")

    fun item(line: String): Pair<Int, Int>? =
        item.find(line)?.let { it.groupValues[1].toInt() to it.groupValues[2].toInt() }

    fun title(line: String): String? = dest.find(line)?.groupValues?.get(1)?.let { path ->
        path.substringAfterLast('/').substringBeforeLast('.')
            .replace(Regex("""\.f\d+$"""), "")
            .replace(Regex("""^\d{3} - """), "")
            .replace(Regex("""\s*\[[^\]]+]$"""), "")
    }

    fun error(output: String?): String {
        val lines = output.orEmpty().lines().map { it.trim() }.filter { it.isNotEmpty() }
        return lines.lastOrNull { it.startsWith("ERROR:") }?.removePrefix("ERROR:")?.trim()
            ?: lines.lastOrNull()
            ?: "yt-dlp error"
    }
}
