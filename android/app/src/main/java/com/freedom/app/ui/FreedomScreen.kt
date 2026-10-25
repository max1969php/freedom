package com.freedom.app.ui

import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.StringRes
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Download
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.freedom.app.MainViewModel
import com.freedom.app.R
import com.freedom.app.download.AUDIO_BITRATES
import com.freedom.app.download.AUDIO_FORMATS
import com.freedom.app.download.Job
import com.freedom.app.download.Kind
import com.freedom.app.download.Mode
import com.freedom.app.download.QUALITIES
import com.freedom.app.download.Sites
import com.freedom.app.download.State
import com.freedom.app.download.VIDEO_CONTAINERS
import com.freedom.app.ui.components.FreedomMark
import com.freedom.app.ui.components.PunkButton
import com.freedom.app.ui.components.Stamp
import com.freedom.app.ui.components.TapeChip
import com.freedom.app.ui.theme.Zine

private enum class Tab(@StringRes val label: Int) {
    DOWNLOAD(R.string.tab_download), QUEUE(R.string.tab_queue), SERVICES(R.string.tab_services), SETUP(R.string.tab_setup)
}

private const val REPO_URL = "https://github.com/max1969php/freedom"
private const val SUPPORTED_URL = "https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md"

@Composable
fun FreedomScreen(vm: MainViewModel, onBeforeDownload: () -> Unit) {
    var tab by rememberSaveable { mutableIntStateOf(0) }
    val jobs by vm.queue.jobs.collectAsState()
    val active = jobs.count { !it.state.finished }
    Column(
        Modifier
            .fillMaxSize()
            .background(Zine.Toner)
            .safeDrawingPadding()
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        ) {
            FreedomMark(size = 40.dp)
            Spacer(Modifier.width(10.dp))
            Text("FREEDOM", style = MaterialTheme.typography.headlineLarge, color = Zine.Paper)
            Spacer(Modifier.weight(1f))
            Stamp(stringResource(R.string.stamp, Sites.SERVICES.size), rotation = -3f)
        }
        TabBar(tab, active) { tab = it }
        Box(Modifier.weight(1f)) {
            when (Tab.entries[tab]) {
                Tab.DOWNLOAD -> DownloadTab(vm) {
                    onBeforeDownload()
                    if (vm.submit() > 0) tab = Tab.QUEUE.ordinal
                }
                Tab.QUEUE -> QueueTab(vm, jobs)
                Tab.SERVICES -> ServicesTab()
                Tab.SETUP -> SetupTab(vm)
            }
        }
    }
}

@Composable
private fun TabBar(selected: Int, active: Int, onSelect: (Int) -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .background(Zine.Paper)
            .padding(vertical = 2.dp)
            .background(Zine.Toner)
    ) {
        Tab.entries.forEachIndexed { i, tab ->
            val on = i == selected
            var label = stringResource(tab.label).uppercase()
            if (tab == Tab.QUEUE && active > 0) label += " $active"
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp)
                    .background(if (on) Zine.Acid else Zine.Toner)
                    .clickable { onSelect(i) },
            ) {
                Text(
                    if (on) "[$label]" else label,
                    style = MaterialTheme.typography.labelMedium,
                    color = if (on) Zine.Toner else Zine.Paper,
                    textAlign = TextAlign.Center,
                    maxLines = 1,
                )
            }
        }
    }
}

@Composable
private fun Section(text: String) {
    Spacer(Modifier.height(18.dp))
    Text(text.uppercase(), style = MaterialTheme.typography.labelLarge, color = Zine.Acid)
    Spacer(Modifier.height(8.dp))
}

@Composable
private fun Muted(text: String) {
    Text(text, style = MaterialTheme.typography.bodySmall, color = Zine.Smudge)
}

@Composable
private fun ChipRow(content: @Composable () -> Unit) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
    ) { content() }
}

@Composable
private fun Toggle(text: String, checked: Boolean, enabled: Boolean = true, onChange: (Boolean) -> Unit) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = enabled) { onChange(!checked) }
            .padding(vertical = 8.dp),
    ) {
        Box(
            Modifier
                .size(18.dp)
                .border(2.dp, if (!enabled) Zine.Concrete else if (checked) Zine.Acid else Zine.Paper)
                .background(if (checked && enabled) Zine.Acid else Color.Transparent)
        )
        Spacer(Modifier.width(12.dp))
        Text(text, style = MaterialTheme.typography.bodyMedium, color = if (enabled) Zine.Paper else Zine.Smudge)
    }
}

@Composable
private fun Field(
    value: String,
    onChange: (String) -> Unit,
    placeholder: String,
    prefix: String? = null,
    singleLine: Boolean = true,
    minHeight: Int = 0,
) {
    Row(
        verticalAlignment = if (singleLine) Alignment.CenterVertically else Alignment.Top,
        modifier = Modifier.fillMaxWidth().border(2.dp, Zine.Paper).padding(horizontal = 12.dp, vertical = 12.dp),
    ) {
        if (prefix != null) {
            Text(prefix, style = MaterialTheme.typography.labelLarge, color = Zine.Acid)
            Spacer(Modifier.width(8.dp))
        }
        Box(Modifier.weight(1f).heightIn(min = minHeight.dp)) {
            if (value.isEmpty()) Text(placeholder, style = MaterialTheme.typography.bodyMedium, color = Zine.Smudge)
            BasicTextField(
                value = value,
                onValueChange = onChange,
                singleLine = singleLine,
                textStyle = MaterialTheme.typography.bodyMedium.merge(TextStyle(color = Zine.Paper)),
                cursorBrush = SolidColor(Zine.Acid),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun Page(content: @Composable ColumnScope.() -> Unit) {
    Column(
        Modifier
            .fillMaxSize()
            .imePadding()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 8.dp),
        content = content,
    )
}

// ------------------------------------------------------------------ SCARICA

@Composable
private fun DownloadTab(vm: MainViewModel, onDownload: () -> Unit) {
    val context = LocalContext.current
    val urls by vm.urls.collectAsState()
    val o by vm.options.collectAsState()
    val items by vm.items.collectAsState()
    val found = remember(urls) { Sites.splitUrls(urls) }
    Page {
        Spacer(Modifier.height(8.dp))
        Field(urls, { vm.urls.value = it }, stringResource(R.string.urls_placeholder), prefix = "URL_", singleLine = false, minHeight = 72)
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth().padding(top = 6.dp)) {
            Text(
                if (found.isEmpty()) stringResource(R.string.recognized_none, Sites.SERVICES.size)
                else stringResource(R.string.recognized, found.size) + "  " +
                    found.groupingBy { Sites.detect(it)?.name ?: "?" }.eachCount().entries
                        .joinToString(" // ") { "${it.key.uppercase()} ×${it.value}" },
                style = MaterialTheme.typography.bodySmall,
                color = Zine.Smudge,
                modifier = Modifier.weight(1f),
            )
            Text(
                stringResource(R.string.paste),
                style = MaterialTheme.typography.labelMedium,
                color = Zine.Paper,
                modifier = Modifier
                    .clickable {
                        val clip = context.getSystemService(ClipboardManager::class.java).primaryClip
                        clip?.getItemAt(0)?.coerceToText(context)?.toString()?.let(vm::addUrls)
                    }
                    .padding(8.dp),
            )
        }

        Section(stringResource(R.string.what))
        ChipRow {
            for ((mode, label) in listOf(Mode.BOTH to R.string.mode_both, Mode.VIDEO to R.string.mode_video, Mode.AUDIO to R.string.mode_audio)) {
                TapeChip(stringResource(label), o.mode == mode, { vm.options.value = o.copy(mode = mode) })
            }
        }
        if (o.mode != Mode.AUDIO) {
            Section(stringResource(R.string.quality))
            ChipRow {
                QUALITIES.forEach { q ->
                    TapeChip(if (q == 0) stringResource(R.string.best) else "${q}p", o.maxHeight == q, { vm.options.value = o.copy(maxHeight = q) })
                }
            }
        }
        if (o.mode == Mode.BOTH) {
            Section(stringResource(R.string.container))
            ChipRow {
                VIDEO_CONTAINERS.forEach { c -> TapeChip(c, o.container == c, { vm.options.value = o.copy(container = c) }) }
            }
        }
        if (o.mode == Mode.AUDIO) {
            Section(stringResource(R.string.audio_format))
            ChipRow {
                AUDIO_FORMATS.forEach { f ->
                    TapeChip(if (f == "best") stringResource(R.string.original) else f, o.audioFormat == f, { vm.options.value = o.copy(audioFormat = f) })
                }
            }
            if (o.audioFormat !in setOf("flac", "wav", "best")) {
                Section(stringResource(R.string.bitrate))
                ChipRow {
                    AUDIO_BITRATES.forEach { b -> TapeChip("$b kbps", o.audioBitrate == b, { vm.options.value = o.copy(audioBitrate = b) }) }
                }
            }
        }

        Section(stringResource(R.string.compilation))
        Toggle(stringResource(R.string.playlist_all), o.playlist) { vm.options.value = o.copy(playlist = it) }
        if (o.playlist) {
            Field(items, { vm.items.value = it }, stringResource(R.string.items_placeholder))
        }

        Section(stringResource(R.string.extras))
        Toggle(stringResource(R.string.subtitles), o.subtitles, enabled = o.mode != Mode.AUDIO) { vm.options.value = o.copy(subtitles = it) }
        Toggle(stringResource(R.string.thumbnail), o.embedThumbnail) { vm.options.value = o.copy(embedThumbnail = it) }
        Toggle(stringResource(R.string.metadata), o.embedMetadata) { vm.options.value = o.copy(embedMetadata = it) }

        Spacer(Modifier.height(20.dp))
        PunkButton(stringResource(R.string.download), onClick = onDownload, icon = Icons.Filled.Download, enabled = found.isNotEmpty())
        Spacer(Modifier.height(12.dp))
        Muted(stringResource(R.string.saved_where))
        Spacer(Modifier.height(4.dp))
        Muted(stringResource(R.string.rights))
        Spacer(Modifier.height(24.dp))
    }
}

// ------------------------------------------------------------------ CODA

@Composable
private fun QueueTab(vm: MainViewModel, jobs: List<Job>) {
    if (jobs.isEmpty()) {
        Box(Modifier.fillMaxSize().padding(32.dp), contentAlignment = Alignment.Center) {
            Text(stringResource(R.string.queue_empty), style = MaterialTheme.typography.bodyMedium, color = Zine.Smudge, textAlign = TextAlign.Center)
        }
        return
    }
    LazyColumn(contentPadding = PaddingValues(vertical = 8.dp)) {
        item {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)) {
                Text(
                    stringResource(R.string.queue_summary, jobs.count { !it.state.finished }, jobs.size).uppercase(),
                    style = MaterialTheme.typography.titleLarge, color = Zine.Paper, modifier = Modifier.weight(1f),
                )
                Text(
                    stringResource(R.string.clear_finished), style = MaterialTheme.typography.labelMedium, color = Zine.Paper,
                    modifier = Modifier.clickable { vm.queue.clearFinished() }.padding(8.dp),
                )
            }
        }
        itemsIndexed(jobs.asReversed(), key = { _, j -> j.id }) { _, job ->
            JobRow(job, onCancel = { vm.queue.cancel(job.id) }, onRetry = { vm.queue.retry(job.id) }, onRemove = { vm.queue.remove(job.id) })
        }
    }
}

@Composable
private fun JobRow(job: Job, onCancel: () -> Unit, onRetry: () -> Unit, onRemove: () -> Unit) {
    val failed = job.state == State.ERROR || job.state == State.PARTIAL
    Column(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 5.dp)
            .border(2.dp, if (failed) Zine.Spray else if (job.state == State.DONE) Zine.Acid else Zine.Concrete)
            .padding(12.dp)
    ) {
        Row {
            Text("%03d".format(job.id), style = MaterialTheme.typography.labelSmall, color = Zine.Spray)
            Spacer(Modifier.width(10.dp))
            Column(Modifier.weight(1f)) {
                Text(
                    job.title.ifEmpty { job.request.url }.uppercase(),
                    style = MaterialTheme.typography.titleMedium, color = Zine.Paper, maxLines = 2, overflow = TextOverflow.Ellipsis,
                )
                val what = when (job.request.mode) {
                    Mode.BOTH -> stringResource(R.string.mode_both)
                    Mode.VIDEO -> stringResource(R.string.mode_video)
                    Mode.AUDIO -> stringResource(R.string.mode_audio)
                }
                val parts = buildList {
                    add(job.service.uppercase()); add(what)
                    if (job.count > 1) add(stringResource(R.string.items_progress, job.index, job.count))
                }
                Text(parts.joinToString(" // "), style = MaterialTheme.typography.bodySmall, color = Zine.Smudge, maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
        }
        Spacer(Modifier.height(6.dp))
        val (label, color) = when (job.state) {
            State.QUEUED -> stringResource(R.string.st_queued) to Zine.Smudge
            State.RUNNING -> stringResource(R.string.st_running, (job.progress * 100).toInt()) +
                (if (job.eta > 0) "  ·  ETA ${job.eta / 60}:${"%02d".format(job.eta % 60)}" else "") to Zine.Acid
            State.PROCESSING -> stringResource(R.string.st_processing) to Zine.Acid
            State.DONE -> "✓ " + stringResource(R.string.st_done, job.saved) to Zine.Acid
            State.PARTIAL -> "◐ " + stringResource(R.string.st_partial, job.saved) + " — " + job.error to Zine.Spray
            State.CANCELLED -> "✕ " + stringResource(R.string.st_cancelled) to Zine.Spray
            State.ERROR -> "✕ " + job.error.ifEmpty { stringResource(R.string.st_error) } to Zine.Spray
        }
        Text(label.uppercase(), style = MaterialTheme.typography.labelSmall, color = color, maxLines = 4)
        if (job.state == State.RUNNING || job.state == State.PROCESSING) {
            Spacer(Modifier.height(6.dp))
            Box(Modifier.fillMaxWidth().height(4.dp).background(Zine.Concrete)) {
                Box(Modifier.fillMaxWidth(job.progress.coerceIn(0f, 1f)).height(4.dp).background(Zine.Acid))
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(18.dp), modifier = Modifier.padding(top = 6.dp)) {
            if (!job.state.finished) Action(stringResource(R.string.cancel), Zine.Spray, onCancel)
            if (failed || job.state == State.CANCELLED) Action(stringResource(R.string.retry), Zine.Paper, onRetry)
            if (job.state.finished) Action(stringResource(R.string.remove), Zine.Paper, onRemove)
        }
    }
}

@Composable
private fun Action(text: String, color: Color, onClick: () -> Unit) {
    Text(text.uppercase(), style = MaterialTheme.typography.labelMedium, color = color, modifier = Modifier.clickable(onClick = onClick).padding(vertical = 6.dp))
}

// ------------------------------------------------------------------ SERVIZI

@Composable
private fun ServicesTab() {
    val context = LocalContext.current
    LazyColumn(contentPadding = PaddingValues(vertical = 8.dp)) {
        item {
            Column(Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
                Text(stringResource(R.string.services_title, Sites.SERVICES.size).uppercase(), style = MaterialTheme.typography.titleLarge, color = Zine.Paper)
                Spacer(Modifier.height(4.dp))
                Muted(stringResource(R.string.services_intro))
            }
        }
        itemsIndexed(Sites.SERVICES) { i, s ->
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)) {
                Text("%03d".format(i + 1), style = MaterialTheme.typography.labelSmall, color = Zine.Spray)
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    Text(s.name.uppercase(), style = MaterialTheme.typography.titleMedium, color = Zine.Paper)
                    Text("${s.domains.first()} // ${s.lists}", style = MaterialTheme.typography.bodySmall, color = Zine.Smudge)
                }
                Text(
                    when (s.kind) { Kind.VIDEO -> "VIDEO"; Kind.AUDIO -> "AUDIO"; Kind.BOTH -> "A+V" },
                    style = MaterialTheme.typography.labelSmall, color = if (s.kind == Kind.AUDIO) Zine.Acid else Zine.Paper,
                )
            }
        }
        item {
            Text(
                "↗ " + stringResource(R.string.services_more),
                style = MaterialTheme.typography.bodyMedium, color = Zine.Acid,
                modifier = Modifier.clickable { open(context, SUPPORTED_URL) }.padding(16.dp),
            )
        }
    }
}

// ------------------------------------------------------------------ SETUP

@Composable
private fun SetupTab(vm: MainViewModel) {
    val context = LocalContext.current
    val engine by vm.engine.collectAsState()
    val status by vm.updateStatus.collectAsState()
    val parallel by vm.parallel.collectAsState()
    val rate by vm.rateLimit.collectAsState()
    val cookies by vm.hasCookies.collectAsState()
    val pickCookies = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri -> uri?.let(vm::importCookies) }
    Page {
        Section(stringResource(R.string.engine))
        Text("yt-dlp $engine // ffmpeg ✓", style = MaterialTheme.typography.bodyMedium, color = Zine.Paper)
        Spacer(Modifier.height(10.dp))
        PunkButton(stringResource(R.string.update_engine), onClick = { vm.updateEngine() })
        status?.let { Spacer(Modifier.height(6.dp)); Muted(it) }

        Section(stringResource(R.string.parallel))
        ChipRow { (1..4).forEach { n -> TapeChip("$n", parallel == n, { vm.setParallel(n) }) } }

        Section(stringResource(R.string.rate_limit))
        Field(rate, { vm.rateLimit.value = it }, stringResource(R.string.rate_placeholder))

        Section(stringResource(R.string.access))
        Muted(stringResource(R.string.cookies_intro))
        Spacer(Modifier.height(10.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            PunkButton(stringResource(R.string.import_cookies), onClick = { pickCookies.launch(arrayOf("text/plain", "*/*")) }, container = Zine.Paper, shadow = Zine.Acid)
            if (cookies) PunkButton(stringResource(R.string.forget_cookies), onClick = vm::clearCookies, container = Zine.Toner, content = Zine.Spray)
        }
        if (cookies) { Spacer(Modifier.height(6.dp)); Muted("✓ cookies.txt") }

        Spacer(Modifier.height(24.dp))
        Box(Modifier.fillMaxWidth().height(2.dp).background(Zine.Paper))
        Spacer(Modifier.height(12.dp))
        Muted(stringResource(R.string.about))
        for ((label, url) in listOf(REPO_URL.removePrefix("https://") to REPO_URL, "github.com/yt-dlp/yt-dlp" to "https://github.com/yt-dlp/yt-dlp")) {
            Text("↗ $label", style = MaterialTheme.typography.bodyMedium, color = Zine.Acid, modifier = Modifier.clickable { open(context, url) }.padding(vertical = 6.dp))
        }
        Spacer(Modifier.height(24.dp))
    }
}

private fun open(context: Context, url: String) {
    runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
}
