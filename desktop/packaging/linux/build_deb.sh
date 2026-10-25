#!/usr/bin/env bash
# Pacchetto .deb per Ubuntu 22.04+ (amd64). Dalla cartella desktop/:  bash packaging/linux/build_deb.sh
# Si installa con:  sudo apt install ./dist/freedom_<versione>_amd64.deb   (apt tira dentro ffmpeg)
set -euo pipefail
cd "$(dirname "$0")/../.."

VERSION=$(sed -n 's/__version__ = "\(.*\)"/\1/p' freedom/__init__.py)
ARCH=$(dpkg --print-architecture)
PY=${PYTHON:-python3}

# uv se c'è (non serve il pacchetto python3-venv), altrimenti venv + pip.
UV=$(command -v uv || true)
if [ ! -x .venv/bin/python ]; then
  if [ -n "$UV" ]; then "$UV" venv -q --python "$PY" .venv; else "$PY" -m venv .venv; fi
fi
if [ -n "$UV" ]; then
  "$UV" pip install -q --python .venv/bin/python -r requirements.txt
else
  .venv/bin/python -m pip install -q -U pip
  .venv/bin/python -m pip install -q -r requirements.txt
fi

# Deno: il runtime JavaScript con cui yt-dlp risolve le challenge di YouTube (senza, mancano formati).
if [ ! -x vendor/deno ]; then
  mkdir -p vendor
  curl -fsSL -o build-deno.zip https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip
  .venv/bin/python -m zipfile -e build-deno.zip vendor/ && rm build-deno.zip
  chmod +x vendor/deno
fi

.venv/bin/python packaging/render_icons.py
.venv/bin/python -m pytest -q tests
.venv/bin/pyinstaller --noconfirm --clean --distpath dist --workpath build/pyinstaller packaging/freedom.spec

PKG=build/deb/freedom_${VERSION}_${ARCH}
rm -rf "$PKG"
mkdir -p "$PKG/DEBIAN" "$PKG/opt" "$PKG/usr/bin" "$PKG/usr/share/applications" "$PKG/usr/share/metainfo"
cp -a dist/freedom "$PKG/opt/freedom"
ln -s /opt/freedom/freedom "$PKG/usr/bin/freedom"
install -m644 packaging/linux/freedom.desktop "$PKG/usr/share/applications/freedom.desktop"
install -m644 packaging/linux/freedom.metainfo.xml "$PKG/usr/share/metainfo/io.github.freedom.metainfo.xml"
for s in 16 24 32 48 64 128 256 512; do
  d="$PKG/usr/share/icons/hicolor/${s}x${s}/apps"
  mkdir -p "$d"
  install -m644 "build/icons/freedom-$s.png" "$d/freedom.png"
done
mkdir -p "$PKG/usr/share/icons/hicolor/scalable/apps"
install -m644 freedom/assets/icon.svg "$PKG/usr/share/icons/hicolor/scalable/apps/freedom.svg"

SIZE=$(du -sk "$PKG" | cut -f1)
cat > "$PKG/DEBIAN/control" <<CONTROL
Package: freedom
Version: ${VERSION}
Section: video
Priority: optional
Architecture: ${ARCH}
Installed-Size: ${SIZE}
Depends: ffmpeg, libegl1, libgl1, libxkbcommon-x11-0, libxcb-cursor0, libxcb-icccm4, libxcb-keysyms1, libxcb-shape0, libfontconfig1, libdbus-1-3
Recommends: fonts-dejavu-core
Maintainer: Freedom <noreply@github.com>
Homepage: https://github.com/max1969php/freedom
Description: Scarica video, audio o entrambi da 1800 siti
 Interfaccia grafica per yt-dlp: YouTube, YouTube Music, Vimeo, Twitch,
 TikTok, SoundCloud, Bandcamp, Mixcloud, Internet Archive, RaiPlay e molti
 altri. Download singoli o a compilation (playlist, album, canali), video
 fino a 4K, audio in MP3, M4A, Opus, FLAC o WAV.
CONTROL
cat > "$PKG/DEBIAN/postinst" <<'POST'
#!/bin/sh
set -e
command -v update-desktop-database >/dev/null && update-desktop-database -q /usr/share/applications || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -t /usr/share/icons/hicolor || true
POST
cp "$PKG/DEBIAN/postinst" "$PKG/DEBIAN/postrm"
chmod 755 "$PKG/DEBIAN/postinst" "$PKG/DEBIAN/postrm"

mkdir -p dist
dpkg-deb --root-owner-group --build "$PKG" "dist/freedom_${VERSION}_${ARCH}.deb"
tar -C dist -czf "dist/freedom-${VERSION}-linux-${ARCH}.tar.gz" freedom
echo "dist/freedom_${VERSION}_${ARCH}.deb"
