package com.freedom.app

import android.app.Application
import com.freedom.app.download.DownloadQueue
import com.freedom.app.download.Engine
import com.freedom.app.download.Prefs
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread

class FreedomApp : Application() {
    lateinit var prefs: Prefs
        private set
    lateinit var queue: DownloadQueue
        private set

    override fun onCreate() {
        super.onCreate()
        prefs = Prefs(this)
        queue = DownloadQueue(this, prefs)
        // Estrae Python/yt-dlp/FFmpeg subito, e una volta al giorno aggiorna yt-dlp.
        thread(name = "engine-init") {
            runCatching { Engine.init(this) }
            if (System.currentTimeMillis() - prefs.updatedAt > TimeUnit.DAYS.toMillis(1)) {
                runCatching { Engine.update(this) }.onSuccess { prefs.updatedAt = System.currentTimeMillis() }
            }
        }
    }
}
