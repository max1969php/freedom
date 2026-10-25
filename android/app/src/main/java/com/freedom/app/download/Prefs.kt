package com.freedom.app.download

import android.content.Context
import java.io.File

class Prefs(context: Context) {
    private val p = context.getSharedPreferences("freedom", Context.MODE_PRIVATE)

    var parallel: Int
        get() = p.getInt("parallel", 2).coerceIn(1, 4)
        set(v) = p.edit().putInt("parallel", v).apply()

    var updatedAt: Long
        get() = p.getLong("updated_at", 0L)
        set(v) = p.edit().putLong("updated_at", v).apply()

    var rateLimit: String
        get() = p.getString("rate_limit", "").orEmpty()
        set(v) = p.edit().putString("rate_limit", v).apply()

    /** Le ultime scelte della scheda SCARICA, per non ripeterle ogni volta. */
    var last: Request
        get() = Request(
            url = "",
            mode = runCatching { Mode.valueOf(p.getString("mode", Mode.BOTH.name)!!) }.getOrDefault(Mode.BOTH),
            maxHeight = p.getInt("quality", 1080),
            container = p.getString("container", "mp4")!!,
            audioFormat = p.getString("audio_format", "mp3")!!,
            audioBitrate = p.getString("bitrate", "320")!!,
            playlist = p.getBoolean("playlist", true),
            subtitles = p.getBoolean("subtitles", false),
            embedThumbnail = p.getBoolean("thumbnail", true),
            embedMetadata = p.getBoolean("metadata", true),
        )
        set(r) = p.edit()
            .putString("mode", r.mode.name).putInt("quality", r.maxHeight).putString("container", r.container)
            .putString("audio_format", r.audioFormat).putString("bitrate", r.audioBitrate)
            .putBoolean("playlist", r.playlist).putBoolean("subtitles", r.subtitles)
            .putBoolean("thumbnail", r.embedThumbnail).putBoolean("metadata", r.embedMetadata)
            .apply()

    fun cookiesFile(context: Context) = File(context.filesDir, "cookies.txt")
}
