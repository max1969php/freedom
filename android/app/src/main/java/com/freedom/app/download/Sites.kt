package com.freedom.app.download

import java.net.URI

enum class Kind { VIDEO, AUDIO, BOTH }

data class Service(val name: String, val domains: List<String>, val kind: Kind, val lists: String)

/** Gli stessi servizi di freedom/sites.py: yt-dlp ne supporta altri 1800. */
object Sites {
    val SERVICES = listOf(
        Service("YouTube", listOf("youtube.com", "youtu.be"), Kind.BOTH, "playlist, canali, Shorts"),
        Service("YouTube Music", listOf("music.youtube.com"), Kind.AUDIO, "album, playlist"),
        Service("Vimeo", listOf("vimeo.com"), Kind.VIDEO, "album, canali, showcase"),
        Service("Dailymotion", listOf("dailymotion.com", "dai.ly"), Kind.VIDEO, "playlist, utenti"),
        Service("Twitch", listOf("twitch.tv"), Kind.VIDEO, "VOD, clip, collezioni"),
        Service("TikTok", listOf("tiktok.com"), Kind.VIDEO, "profili, hashtag"),
        Service("Instagram", listOf("instagram.com"), Kind.VIDEO, "post multipli, reel"),
        Service("Facebook", listOf("facebook.com", "fb.watch"), Kind.VIDEO, "video, reel"),
        Service("X / Twitter", listOf("x.com", "twitter.com"), Kind.VIDEO, "thread con più video"),
        Service("Reddit", listOf("reddit.com", "redd.it"), Kind.VIDEO, "post"),
        Service("SoundCloud", listOf("soundcloud.com"), Kind.AUDIO, "set, profili, like"),
        Service("Bandcamp", listOf("bandcamp.com"), Kind.AUDIO, "album, discografie"),
        Service("Mixcloud", listOf("mixcloud.com"), Kind.AUDIO, "profili, playlist"),
        Service("Audiomack", listOf("audiomack.com"), Kind.AUDIO, "album, playlist"),
        Service("Internet Archive", listOf("archive.org"), Kind.BOTH, "collezioni"),
        Service("Bilibili", listOf("bilibili.com", "b23.tv"), Kind.VIDEO, "serie, playlist"),
        Service("Niconico", listOf("nicovideo.jp"), Kind.VIDEO, "mylist, serie"),
        Service("Rumble", listOf("rumble.com"), Kind.VIDEO, "canali"),
        Service("Odysee", listOf("odysee.com"), Kind.VIDEO, "canali, playlist"),
        Service("PeerTube", listOf("framatube.org", "peertube.tv", "tilvids.com"), Kind.VIDEO, "canali, playlist"),
        Service("Bitchute", listOf("bitchute.com"), Kind.VIDEO, "canali"),
        Service("Streamable", listOf("streamable.com"), Kind.VIDEO, "singoli"),
        Service("TED", listOf("ted.com"), Kind.VIDEO, "playlist"),
        Service("RaiPlay", listOf("raiplay.it"), Kind.VIDEO, "programmi"),
        Service("RaiPlay Sound", listOf("raiplaysound.it"), Kind.AUDIO, "podcast, programmi"),
        Service("ARTE", listOf("arte.tv"), Kind.VIDEO, "collezioni"),
        Service("Spreaker", listOf("spreaker.com"), Kind.AUDIO, "podcast"),
        Service("Kick", listOf("kick.com"), Kind.VIDEO, "VOD, clip"),
    )

    fun detect(url: String): Service? {
        val host = runCatching { URI(url.trim()).host }.getOrNull()?.lowercase()
            ?.removePrefix("www.")?.removePrefix("m.") ?: return null
        return SERVICES.flatMap { s -> s.domains.map { d -> s to d } }
            .filter { (_, d) -> host == d || host.endsWith(".$d") }
            .maxByOrNull { (_, d) -> d.length }?.first
    }

    fun hostOf(url: String): String =
        runCatching { URI(url).host }.getOrNull()?.removePrefix("www.") ?: "?"

    fun splitUrls(text: String): List<String> {
        val seen = LinkedHashSet<String>()
        for (raw in text.replace(",", " ").split(Regex("\\s+"))) {
            val t = raw.trim().trim('<', '>', '"', '\'')
            when {
                t.startsWith("http://") || t.startsWith("https://") -> seen += t
                '.' in t && '/' in t -> seen += "https://$t"
            }
        }
        return seen.toList()
    }
}
