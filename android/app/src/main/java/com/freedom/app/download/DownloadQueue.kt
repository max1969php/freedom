package com.freedom.app.download

import android.content.ContentValues
import android.content.Context
import android.media.MediaScannerConnection
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.webkit.MimeTypeMap
import androidx.core.content.ContextCompat
import com.yausername.ffmpeg.FFmpeg
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import java.io.File
import java.util.concurrent.atomic.AtomicLong

enum class State { QUEUED, RUNNING, PROCESSING, DONE, PARTIAL, ERROR, CANCELLED;
    val finished get() = this == DONE || this == PARTIAL || this == ERROR || this == CANCELLED
}

data class Job(
    val id: Long,
    val request: Request,
    val service: String,
    val state: State = State.QUEUED,
    val title: String = "",
    val progress: Float = 0f,
    val eta: Long = -1,
    val index: Int = 0,
    val count: Int = 0,
    val saved: Int = 0,
    val error: String = "",
)

/** yt-dlp + Python + FFmpeg dentro l'APK, via youtubedl-android. La prima init estrae ~60 MB. */
object Engine {
    @Volatile private var ready = false

    @Synchronized
    fun init(context: Context) {
        if (ready) return
        YoutubeDL.getInstance().init(context)
        FFmpeg.getInstance().init(context)
        ready = true
    }

    fun version(context: Context): String =
        runCatching { YoutubeDL.getInstance().versionName(context) ?: YoutubeDL.getInstance().version(context) }
            .getOrNull() ?: "—"

    /** I siti cambiano spesso: si scarica l'ultima yt-dlp stabile. Restituisce la versione installata. */
    fun update(context: Context): String {
        init(context)
        YoutubeDL.getInstance().updateYoutubeDL(context, YoutubeDL.UpdateChannel._STABLE)
        return version(context)
    }
}

class DownloadQueue(private val context: Context, private val prefs: Prefs) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val ids = AtomicLong(1)
    private val _jobs = MutableStateFlow<List<Job>>(emptyList())
    val jobs: StateFlow<List<Job>> = _jobs
    private var permits = Semaphore(prefs.parallel)

    fun setParallel(n: Int) {
        prefs.parallel = n
        permits = Semaphore(n)
    }

    fun submit(requests: List<Request>) {
        val new = requests.map { r ->
            Job(id = ids.getAndIncrement(), request = r, service = Sites.detect(r.url)?.name ?: Sites.hostOf(r.url))
        }
        _jobs.update { it + new }
        ContextCompat.startForegroundService(context, DownloadService.intent(context))
        new.forEach { job -> scope.launch { permits.withPermit { run(job.id) } } }
    }

    fun cancel(id: Long) {
        val job = get(id) ?: return
        if (job.state.finished) return
        set(id) { it.copy(state = State.CANCELLED) }
        runCatching { YoutubeDL.getInstance().destroyProcessById(processId(id)) }
    }

    fun retry(id: Long) {
        val job = get(id) ?: return
        remove(id)
        submit(listOf(job.request))
    }

    fun remove(id: Long) = _jobs.update { list -> list.filterNot { it.id == id && it.state.finished } }

    fun clearFinished() = _jobs.update { list -> list.filterNot { it.state.finished } }

    fun active() = _jobs.value.count { !it.state.finished }

    private fun get(id: Long) = _jobs.value.firstOrNull { it.id == id }

    private fun set(id: Long, change: (Job) -> Job) =
        _jobs.update { list -> list.map { if (it.id == id) change(it) else it } }

    private fun processId(id: Long) = "freedom-$id"

    private fun run(id: Long) {
        val job = get(id) ?: return
        if (job.state != State.QUEUED) return
        set(id) { it.copy(state = State.RUNNING) }
        val dir = File(context.cacheDir, "jobs/$id").apply { deleteRecursively(); mkdirs() }
        val doneLog = File(dir, ".done")
        var failure: String? = null
        try {
            Engine.init(context)
            val cookies = prefs.cookiesFile(context).takeIf { it.exists() }?.absolutePath
            val request = YoutubeDLRequest(job.request.url).apply {
                addCommands(Options.args(job.request, dir.absolutePath, doneLog.absolutePath, cookies))
            }
            YoutubeDL.getInstance().execute(request, processId(id)) { progress, eta, line ->
                onLine(id, progress, eta, line)
            }
        } catch (e: Exception) {
            failure = OutputParser.error(e.message)
        }
        val files = doneLog.takeIf { it.exists() }?.readLines()?.map { it.trim() }?.filter { it.isNotEmpty() }
            ?.distinct()?.map(::File)?.filter { it.exists() }.orEmpty()
        var saved = 0
        for (f in files) {
            runCatching { save(f, dir) }.onSuccess { saved++ }.onFailure { failure = it.message ?: failure }
        }
        dir.deleteRecursively()
        set(id) { cur ->
            val state = when {
                cur.state == State.CANCELLED -> State.CANCELLED
                saved == 0 -> State.ERROR
                failure != null -> State.PARTIAL
                else -> State.DONE
            }
            cur.copy(state = state, saved = saved, progress = 1f, error = failure.orEmpty())
        }
    }

    private fun onLine(id: Long, progress: Float, eta: Long, line: String) {
        set(id) { cur ->
            if (cur.state == State.CANCELLED) return@set cur
            var next = cur
            OutputParser.item(line)?.let { (i, n) -> next = next.copy(index = i, count = n) }
            OutputParser.title(line)?.let { next = next.copy(title = it) }
            val processing = line.startsWith("[Merger]") || line.startsWith("[ExtractAudio]") ||
                line.startsWith("[EmbedThumbnail]") || line.startsWith("[Metadata]")
            next.copy(
                state = if (processing) State.PROCESSING else State.RUNNING,
                progress = if (progress >= 0) progress / 100f else next.progress,
                eta = eta,
            )
        }
    }

    /** Dal temporaneo del job a Download/Freedom/…, mantenendo la cartella della playlist. */
    private fun save(file: File, jobDir: File) {
        val rel = file.parentFile!!.relativeTo(jobDir).path
        val sub = if (rel.isEmpty() || rel == ".") "Freedom" else "Freedom/$rel"
        val ext = file.extension.lowercase()
        val mime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext) ?: when (ext) {
            "opus" -> "audio/ogg"; "mkv" -> "video/x-matroska"; else -> "application/octet-stream"
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, file.name)
                put(MediaStore.MediaColumns.MIME_TYPE, mime)
                put(MediaStore.MediaColumns.RELATIVE_PATH, "${Environment.DIRECTORY_DOWNLOADS}/$sub")
                put(MediaStore.MediaColumns.IS_PENDING, 1)
            }
            val resolver = context.contentResolver
            val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                ?: error("MediaStore: impossibile creare ${file.name}")
            resolver.openOutputStream(uri)!!.use { out -> file.inputStream().use { it.copyTo(out) } }
            values.clear()
            values.put(MediaStore.MediaColumns.IS_PENDING, 0)
            resolver.update(uri, values, null, null)
        } else {
            @Suppress("DEPRECATION")
            val target = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "$sub/${file.name}")
            target.parentFile?.mkdirs()
            file.copyTo(target, overwrite = true)
            MediaScannerConnection.scanFile(context, arrayOf(target.absolutePath), arrayOf(mime), null)
        }
    }
}
