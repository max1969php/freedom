from __future__ import annotations

from PySide6.QtCore import QLocale

LANGUAGES = {"it": "Italiano", "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch"}

IT = {
    "tagline": "video, audio o entrambi // da soli o a compilation",
    "stamp": "{n} SERVIZI + 1800 SITI",
    "tab_download": "Scarica", "tab_queue": "Coda", "tab_services": "Servizi", "tab_setup": "Setup",
    "paste": "INCOLLA", "clear": "SVUOTA",
    "urls_placeholder": "Uno o più link, uno per riga (o separati da spazi): video, playlist, album, canali, profili…\n"
                        "Puoi anche trascinarli qui sopra.",
    "recognized_none": "Incolla un link: {n} servizi riconosciuti, e tutti i siti di yt-dlp.",
    "recognized": "{n} link →", "other_site": "altro sito",
    "what": "COSA", "mode_both": "Video+Audio", "mode_video": "Solo video", "mode_audio": "Solo audio",
    "quality": "QUALITÀ", "container": "FORMATO", "audio_format": "FORMATO AUDIO", "bitrate": "BITRATE",
    "best": "MIGLIORE", "original": "ORIGINALE",
    "compilation": "COMPILATION",
    "playlist_all": "Se il link è una playlist, un album o un canale, scarica tutte le voci",
    "items_placeholder": "tutte (es. 1-10,15,20-)", "items_hint": "quali voci",
    "extras": "EXTRA", "subtitles": "Sottotitoli", "thumbnail": "Copertina", "metadata": "Metadati e capitoli",
    "save_in": "SALVA IN", "browse": "Sfoglia", "download": "Scarica",
    "rights": "Scarica solo ciò che hai il diritto di scaricare: i termini di alcuni servizi lo vietano.",
    "cancel": "ANNULLA", "retry": "RIPROVA", "open_folder": "APRI CARTELLA", "remove": "TOGLI",
    "items_progress": "{done}/{total} voci",
    "st_queued": "in coda", "st_running": "scarico {p}%", "st_processing": "elaboro con ffmpeg…",
    "st_done": "fatto: {n} file", "st_partial": "{done} fatti, {failed} saltati", "st_cancelled": "annullato",
    "st_error": "errore",
    "clear_finished": "PULISCI FINITI", "queue_empty": "Coda vuota. Vai su SCARICA e incolla un link.",
    "queue_summary": "{active} attivi su {total}",
    "services_title": "{n} servizi provati",
    "services_intro": "Qui sotto i servizi più usati, singoli o a compilation. Il motore è yt-dlp: funziona anche "
                      "con altri 1800 siti, basta incollare il link. I contenuti protetti da DRM (Netflix, Spotify, "
                      "Disney+…) non si possono scaricare.",
    "kind_video": "VIDEO", "kind_audio": "AUDIO", "kind_both": "VIDEO + AUDIO",
    "services_more": "TUTTI I SITI SUPPORTATI DA YT-DLP",
    "engine": "Motore", "update_engine": "Aggiorna yt-dlp",
    "ffmpeg_ok": "ffmpeg ✓", "ffmpeg_missing": "ffmpeg ✕ (installalo: serve per unire video e audio e convertire)",
    "updating": "Scarico l'ultima versione di yt-dlp…", "up_to_date": "Già all'ultima versione.",
    "updated": "Aggiornato a {v}: riavvia Freedom per usarlo.",
    "downloads": "Download", "parallel": "IN PARALLELO", "rate_limit": "LIMITE DI BANDA",
    "rate_placeholder": "nessuno (es. 2M, 500K)",
    "access": "Accesso",
    "cookies_intro": "Per contenuti riservati agli iscritti, con limite d'età o quando un sito chiede di "
                     "confermare di non essere un bot: usa i cookie di un browser in cui hai fatto l'accesso, "
                     "oppure un file cookies.txt (formato Netscape). Meglio un account secondario.",
    "cookies_browser": "COOKIE DAL BROWSER", "cookies_file": "FILE COOKIES.TXT", "none": "Nessuno",
    "language": "Lingua", "system_language": "Lingua del sistema",
    "restart_needed": "La lingua cambia al prossimo avvio.",
    "about": "Freedom {v}. Software libero (GPL-3.0). Motore yt-dlp (Unlicense), conversioni FFmpeg, "
             "interfaccia Qt (LGPL). Nessun account, nessun tracciamento.",
    "quit_active": "Ci sono {n} download in corso. Uscire e annullarli?",
}

EN = {
    "tagline": "video, audio or both // one at a time or whole compilations",
    "stamp": "{n} SERVICES + 1800 SITES",
    "tab_download": "Download", "tab_queue": "Queue", "tab_services": "Services", "tab_setup": "Setup",
    "paste": "PASTE", "clear": "CLEAR",
    "urls_placeholder": "One or more links, one per line (or space separated): videos, playlists, albums, channels…\n"
                        "You can also drag them here.",
    "recognized_none": "Paste a link: {n} known services, plus every yt-dlp site.",
    "recognized": "{n} links →", "other_site": "other site",
    "what": "WHAT", "mode_both": "Video+Audio", "mode_video": "Video only", "mode_audio": "Audio only",
    "quality": "QUALITY", "container": "FORMAT", "audio_format": "AUDIO FORMAT", "bitrate": "BITRATE",
    "best": "BEST", "original": "ORIGINAL",
    "compilation": "COMPILATION",
    "playlist_all": "If the link is a playlist, album or channel, download every item",
    "items_placeholder": "all (e.g. 1-10,15,20-)", "items_hint": "which items",
    "extras": "EXTRAS", "subtitles": "Subtitles", "thumbnail": "Cover art", "metadata": "Metadata and chapters",
    "save_in": "SAVE TO", "browse": "Browse", "download": "Download",
    "rights": "Only download what you have the right to: some services' terms forbid it.",
    "cancel": "CANCEL", "retry": "RETRY", "open_folder": "OPEN FOLDER", "remove": "REMOVE",
    "items_progress": "{done}/{total} items",
    "st_queued": "queued", "st_running": "downloading {p}%", "st_processing": "processing with ffmpeg…",
    "st_done": "done: {n} files", "st_partial": "{done} done, {failed} skipped", "st_cancelled": "cancelled",
    "st_error": "error",
    "clear_finished": "CLEAR FINISHED", "queue_empty": "Queue is empty. Go to DOWNLOAD and paste a link.",
    "queue_summary": "{active} active of {total}",
    "services_title": "{n} tested services",
    "services_intro": "The most used services, single items or compilations. The engine is yt-dlp: it also works "
                      "with 1800 more sites, just paste the link. DRM-protected content (Netflix, Spotify, "
                      "Disney+…) cannot be downloaded.",
    "kind_video": "VIDEO", "kind_audio": "AUDIO", "kind_both": "VIDEO + AUDIO",
    "services_more": "ALL SITES SUPPORTED BY YT-DLP",
    "engine": "Engine", "update_engine": "Update yt-dlp",
    "ffmpeg_ok": "ffmpeg ✓", "ffmpeg_missing": "ffmpeg ✕ (install it: needed to merge video+audio and convert)",
    "updating": "Fetching the latest yt-dlp…", "up_to_date": "Already up to date.",
    "updated": "Updated to {v}: restart Freedom to use it.",
    "downloads": "Downloads", "parallel": "PARALLEL", "rate_limit": "BANDWIDTH LIMIT",
    "rate_placeholder": "none (e.g. 2M, 500K)",
    "access": "Access",
    "cookies_intro": "For members-only or age-restricted content, or when a site asks you to confirm you are not "
                     "a bot: use the cookies of a browser where you are signed in, or a cookies.txt file "
                     "(Netscape format). A secondary account is safer.",
    "cookies_browser": "BROWSER COOKIES", "cookies_file": "COOKIES.TXT FILE", "none": "None",
    "language": "Language", "system_language": "System language",
    "restart_needed": "The language changes on next start.",
    "about": "Freedom {v}. Free software (GPL-3.0). yt-dlp engine (Unlicense), FFmpeg conversions, "
             "Qt interface (LGPL). No accounts, no tracking.",
    "quit_active": "{n} downloads are running. Quit and cancel them?",
}

ES = {
    "tagline": "vídeo, audio o ambos // de uno en uno o en recopilaciones",
    "stamp": "{n} SERVICIOS + 1800 SITIOS",
    "tab_download": "Descargar", "tab_queue": "Cola", "tab_services": "Servicios", "tab_setup": "Ajustes",
    "paste": "PEGAR", "clear": "VACIAR",
    "urls_placeholder": "Uno o más enlaces, uno por línea: vídeos, listas, álbumes, canales…\nTambién puedes arrastrarlos aquí.",
    "recognized_none": "Pega un enlace: {n} servicios conocidos y todos los sitios de yt-dlp.",
    "recognized": "{n} enlaces →", "other_site": "otro sitio",
    "what": "QUÉ", "mode_both": "Vídeo+Audio", "mode_video": "Solo vídeo", "mode_audio": "Solo audio",
    "quality": "CALIDAD", "container": "FORMATO", "audio_format": "FORMATO DE AUDIO", "best": "LA MEJOR",
    "compilation": "RECOPILACIÓN",
    "playlist_all": "Si el enlace es una lista, un álbum o un canal, descarga todo",
    "items_placeholder": "todos (p. ej. 1-10,15,20-)", "items_hint": "qué elementos",
    "subtitles": "Subtítulos", "thumbnail": "Portada", "metadata": "Metadatos y capítulos",
    "save_in": "GUARDAR EN", "browse": "Examinar", "download": "Descargar",
    "rights": "Descarga solo lo que tengas derecho a descargar.",
    "cancel": "CANCELAR", "retry": "REINTENTAR", "open_folder": "ABRIR CARPETA", "remove": "QUITAR",
    "st_queued": "en cola", "st_running": "descargando {p}%", "st_processing": "procesando con ffmpeg…",
    "st_done": "hecho: {n} archivos", "st_partial": "{done} hechos, {failed} omitidos", "st_cancelled": "cancelado",
    "clear_finished": "LIMPIAR TERMINADOS", "queue_empty": "Cola vacía. Ve a DESCARGAR y pega un enlace.",
    "queue_summary": "{active} activos de {total}", "services_title": "{n} servicios probados",
    "update_engine": "Actualizar yt-dlp", "engine": "Motor", "downloads": "Descargas", "parallel": "EN PARALELO",
    "access": "Acceso", "language": "Idioma", "system_language": "Idioma del sistema",
    "restart_needed": "El idioma cambia en el próximo inicio.",
    "quit_active": "Hay {n} descargas en curso. ¿Salir y cancelarlas?",
}

FR = {
    "tagline": "vidéo, audio ou les deux // un par un ou en compilations",
    "stamp": "{n} SERVICES + 1800 SITES",
    "tab_download": "Télécharger", "tab_queue": "File", "tab_services": "Services", "tab_setup": "Réglages",
    "paste": "COLLER", "clear": "VIDER",
    "urls_placeholder": "Un ou plusieurs liens, un par ligne : vidéos, playlists, albums, chaînes…\nVous pouvez aussi les glisser ici.",
    "recognized_none": "Collez un lien : {n} services connus et tous les sites de yt-dlp.",
    "recognized": "{n} liens →", "other_site": "autre site",
    "what": "QUOI", "mode_both": "Vidéo+Audio", "mode_video": "Vidéo seule", "mode_audio": "Audio seul",
    "quality": "QUALITÉ", "container": "FORMAT", "audio_format": "FORMAT AUDIO", "best": "MEILLEURE",
    "compilation": "COMPILATION",
    "playlist_all": "Si le lien est une playlist, un album ou une chaîne, tout télécharger",
    "items_placeholder": "tous (ex. 1-10,15,20-)", "items_hint": "quels éléments",
    "subtitles": "Sous-titres", "thumbnail": "Pochette", "metadata": "Métadonnées et chapitres",
    "save_in": "ENREGISTRER DANS", "browse": "Parcourir", "download": "Télécharger",
    "rights": "Ne téléchargez que ce que vous avez le droit de télécharger.",
    "cancel": "ANNULER", "retry": "RÉESSAYER", "open_folder": "OUVRIR LE DOSSIER", "remove": "RETIRER",
    "st_queued": "en attente", "st_running": "téléchargement {p}%", "st_processing": "traitement ffmpeg…",
    "st_done": "terminé : {n} fichiers", "st_partial": "{done} faits, {failed} ignorés", "st_cancelled": "annulé",
    "clear_finished": "EFFACER TERMINÉS", "queue_empty": "File vide. Allez dans TÉLÉCHARGER et collez un lien.",
    "queue_summary": "{active} actifs sur {total}", "services_title": "{n} services testés",
    "update_engine": "Mettre à jour yt-dlp", "engine": "Moteur", "downloads": "Téléchargements",
    "parallel": "EN PARALLÈLE", "access": "Accès", "language": "Langue", "system_language": "Langue du système",
    "restart_needed": "La langue change au prochain démarrage.",
    "quit_active": "{n} téléchargements en cours. Quitter et les annuler ?",
}

DE = {
    "tagline": "Video, Audio oder beides // einzeln oder als Sammlung",
    "stamp": "{n} DIENSTE + 1800 SEITEN",
    "tab_download": "Laden", "tab_queue": "Warteschlange", "tab_services": "Dienste", "tab_setup": "Setup",
    "paste": "EINFÜGEN", "clear": "LEEREN",
    "urls_placeholder": "Ein oder mehrere Links, einer pro Zeile: Videos, Playlists, Alben, Kanäle…\nDu kannst sie auch hierher ziehen.",
    "recognized_none": "Link einfügen: {n} bekannte Dienste und alle yt-dlp-Seiten.",
    "recognized": "{n} Links →", "other_site": "andere Seite",
    "what": "WAS", "mode_both": "Video+Audio", "mode_video": "Nur Video", "mode_audio": "Nur Audio",
    "quality": "QUALITÄT", "container": "FORMAT", "audio_format": "AUDIOFORMAT", "best": "BESTE",
    "compilation": "SAMMLUNG",
    "playlist_all": "Ist der Link eine Playlist, ein Album oder ein Kanal, alles laden",
    "items_placeholder": "alle (z. B. 1-10,15,20-)", "items_hint": "welche Einträge",
    "subtitles": "Untertitel", "thumbnail": "Cover", "metadata": "Metadaten und Kapitel",
    "save_in": "SPEICHERN IN", "browse": "Durchsuchen", "download": "Laden",
    "rights": "Lade nur, was du laden darfst.",
    "cancel": "ABBRECHEN", "retry": "WIEDERHOLEN", "open_folder": "ORDNER ÖFFNEN", "remove": "ENTFERNEN",
    "st_queued": "wartet", "st_running": "lade {p}%", "st_processing": "verarbeite mit ffmpeg…",
    "st_done": "fertig: {n} Dateien", "st_partial": "{done} fertig, {failed} übersprungen", "st_cancelled": "abgebrochen",
    "clear_finished": "FERTIGE ENTFERNEN", "queue_empty": "Warteschlange leer. Geh zu LADEN und füge einen Link ein.",
    "queue_summary": "{active} aktiv von {total}", "services_title": "{n} getestete Dienste",
    "update_engine": "yt-dlp aktualisieren", "engine": "Engine", "downloads": "Downloads", "parallel": "PARALLEL",
    "access": "Zugang", "language": "Sprache", "system_language": "Systemsprache",
    "restart_needed": "Die Sprache ändert sich beim nächsten Start.",
    "quit_active": "{n} Downloads laufen. Beenden und abbrechen?",
}

_TABLES = {"it": IT, "en": EN, "es": ES, "fr": FR, "de": DE}
_current = IT


def set_language(code: str = "") -> str:
    global _current
    if not code:
        code = QLocale.system().name().split("_")[0]
    _current = _TABLES.get(code, EN)
    return code if code in _TABLES else "en"


def tr(key: str, **kw) -> str:
    text = _current.get(key) or EN.get(key) or IT.get(key) or key
    return text.format(**kw) if kw else text
