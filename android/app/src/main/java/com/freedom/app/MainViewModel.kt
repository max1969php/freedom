package com.freedom.app

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.freedom.app.download.Engine
import com.freedom.app.download.Request
import com.freedom.app.download.Sites
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class MainViewModel(app: Application) : AndroidViewModel(app) {
    private val freedom = app as FreedomApp
    private val prefs = freedom.prefs
    val queue = freedom.queue

    val urls = MutableStateFlow("")
    val options = MutableStateFlow(prefs.last)
    val items = MutableStateFlow("")
    val rateLimit = MutableStateFlow(prefs.rateLimit)
    val parallel = MutableStateFlow(prefs.parallel)

    private val _engine = MutableStateFlow("…")
    val engine: StateFlow<String> = _engine
    private val _updateStatus = MutableStateFlow<String?>(null)
    val updateStatus: StateFlow<String?> = _updateStatus
    private val _hasCookies = MutableStateFlow(prefs.cookiesFile(app).exists())
    val hasCookies: StateFlow<Boolean> = _hasCookies

    init {
        refreshEngine()
    }

    fun addUrls(text: String) {
        val found = Sites.splitUrls(text)
        if (found.isEmpty()) return
        urls.update { cur ->
            val existing = Sites.splitUrls(cur).toSet()
            val new = found.filterNot { it in existing }
            (cur.trimEnd().lines().filter { it.isNotBlank() } + new).joinToString("\n")
        }
    }

    fun submit(): Int {
        val list = Sites.splitUrls(urls.value)
        if (list.isEmpty()) return 0
        val o = options.value
        prefs.last = o
        prefs.rateLimit = rateLimit.value
        queue.submit(list.map { o.copy(url = it, playlistItems = items.value, rateLimit = rateLimit.value) })
        urls.value = ""
        items.value = ""
        return list.size
    }

    fun setParallel(n: Int) {
        parallel.value = n
        queue.setParallel(n)
    }

    fun refreshEngine() = viewModelScope.launch(Dispatchers.IO) {
        runCatching { Engine.init(getApplication()) }
        _engine.value = Engine.version(getApplication())
    }

    fun updateEngine() = viewModelScope.launch(Dispatchers.IO) {
        _updateStatus.value = getApplication<Application>().getString(R.string.updating)
        _updateStatus.value = runCatching { Engine.update(getApplication()) }.fold(
            onSuccess = { v ->
                prefs.updatedAt = System.currentTimeMillis()
                _engine.value = v
                "✓ yt-dlp $v"
            },
            onFailure = { "✕ ${it.message}" },
        )
    }

    fun importCookies(uri: Uri) = viewModelScope.launch(Dispatchers.IO) {
        val app = getApplication<Application>()
        runCatching {
            app.contentResolver.openInputStream(uri)!!.use { input ->
                prefs.cookiesFile(app).outputStream().use { input.copyTo(it) }
            }
        }
        _hasCookies.value = prefs.cookiesFile(app).exists()
    }

    fun clearCookies() {
        prefs.cookiesFile(getApplication()).delete()
        _hasCookies.value = false
    }
}
