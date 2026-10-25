package com.freedom.app.download

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import com.freedom.app.FreedomApp
import com.freedom.app.MainActivity
import com.freedom.app.R
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.launch

/** Tiene vivo il processo finché la coda lavora, anche con lo schermo spento o l'app chiusa. */
@OptIn(FlowPreview::class)
class DownloadService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var watcher: kotlinx.coroutines.Job? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL, getString(R.string.notif_channel), NotificationManager.IMPORTANCE_LOW)
            )
        }
        val queue = (application as FreedomApp).queue
        ServiceCompat.startForeground(
            this, NOTIF_ID, build(queue.jobs.value),
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC else 0,
        )
        if (watcher == null) {
            watcher = scope.launch {
                queue.jobs.debounce(500).collect { jobs ->
                    if (jobs.none { !it.state.finished }) {
                        ServiceCompat.stopForeground(this@DownloadService, ServiceCompat.STOP_FOREGROUND_REMOVE)
                        manager.notify(DONE_ID, done(jobs))
                        stopSelf()
                    } else {
                        manager.notify(NOTIF_ID, build(jobs))
                    }
                }
            }
        }
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }

    private fun open(): PendingIntent = PendingIntent.getActivity(
        this, 0, Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
    )

    private fun build(jobs: List<Job>): Notification {
        val active = jobs.filter { !it.state.finished }
        val current = active.firstOrNull { it.state != State.QUEUED }
        val title = getString(R.string.notif_active, active.size)
        val b = NotificationCompat.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(current?.title?.ifEmpty { current.request.url } ?: getString(R.string.st_queued))
            .setContentIntent(open())
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setColor(0xFFD7FF1F.toInt())
        if (current != null) b.setProgress(100, (current.progress * 100).toInt(), current.state == State.PROCESSING)
        return b.build()
    }

    private fun done(jobs: List<Job>): Notification {
        val files = jobs.sumOf { it.saved }
        val failed = jobs.count { it.state == State.ERROR || it.state == State.PARTIAL }
        return NotificationCompat.Builder(this, CHANNEL)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(getString(R.string.notif_done, files))
            .setContentText(if (failed > 0) getString(R.string.notif_failed, failed) else getString(R.string.notif_where))
            .setContentIntent(open())
            .setAutoCancel(true)
            .setColor(0xFFD7FF1F.toInt())
            .build()
    }

    companion object {
        private const val CHANNEL = "downloads"
        private const val NOTIF_ID = 1
        private const val DONE_ID = 2
        fun intent(context: Context) = Intent(context, DownloadService::class.java)
    }
}
