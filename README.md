# Freedom

Scarica **video, audio o entrambi** da YouTube, YouTube Music, Vimeo, Twitch, TikTok, Instagram,
SoundCloud, Bandcamp, Mixcloud, Internet Archive, RaiPlay e altri ~1800 siti, **un link alla volta
o a compilation** (playlist, album, canali). Motore: [yt-dlp](https://github.com/yt-dlp/yt-dlp) +
FFmpeg. Nessun account, nessun server di mezzo, nessun tracciamento.

| | Pacchetto |
|---|---|
| Windows 10 / 11 | `Freedom-<ver>-windows-x64-setup.exe` |
| Ubuntu 22.04+ | `freedom_<ver>_amd64.deb` → `sudo apt install ./freedom_<ver>_amd64.deb` |
| Android 8+ | `freedom.apk` |

Le Release si creano da sole con un tag `v*` (GitHub Actions: `.github/workflows/build.yml`).

## Struttura

- `desktop/`: Python + PySide6 (Qt 6), una sola app per Windows e Linux; packaging in
  `desktop/packaging/` (PyInstaller, Inno Setup, .deb).
- `android/`: Kotlin + Jetpack Compose + youtubedl-android (yt-dlp, Python e FFmpeg sul telefono).

## Build veloce

```bash
# desktop: test e avvio
cd desktop && uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m pytest -q tests && .venv/bin/python -m freedom

# Ubuntu: .deb in desktop/dist/
bash desktop/packaging/linux/build_deb.sh

# Windows (PowerShell, nella cartella desktop): installer in desktop\dist\
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1

# Android (JDK 17 + Android SDK 34): APK in android/app/build/outputs/apk/release/
cd android && ./gradlew testDebugUnitTest assembleRelease
```

Scarica solo ciò che hai il diritto di scaricare. I contenuti con DRM non sono scaricabili.

Licenza: GPL-3.0-or-later.
