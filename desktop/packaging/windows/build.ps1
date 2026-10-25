# Build completa per Windows 10/11: exe + ffmpeg + installer. Da PowerShell, nella cartella desktop\:
#   powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
# Serve Python 3.12 x64. Inno Setup 6 viene installato con winget se manca.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")

$version = (Select-String -Path freedom\__init__.py -Pattern '"(.+)"').Matches[0].Groups[1].Value

python -m venv .venv-win
.\.venv-win\Scripts\python -m pip install -U pip
.\.venv-win\Scripts\python -m pip install -r requirements.txt

# FFmpeg statico (build GPL di BtbN, aggiornata ogni giorno): unisce video+audio e converte l'audio.
if (-not (Test-Path vendor\ffmpeg.exe)) {
    New-Item -ItemType Directory -Force vendor | Out-Null
    $zip = "$env:TEMP\ffmpeg-win64.zip"
    Invoke-WebRequest "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile $zip
    $tmp = "$env:TEMP\ffmpeg-win64"
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Expand-Archive $zip -DestinationPath $tmp
    Copy-Item (Get-ChildItem $tmp -Recurse -Filter ffmpeg.exe | Select-Object -First 1).FullName vendor\
    Copy-Item (Get-ChildItem $tmp -Recurse -Filter ffprobe.exe | Select-Object -First 1).FullName vendor\
}

# Deno: il runtime JavaScript con cui yt-dlp risolve le challenge di YouTube (senza, mancano formati).
if (-not (Test-Path vendor\deno.exe)) {
    $zip = "$env:TEMP\deno-win64.zip"
    Invoke-WebRequest "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip" -OutFile $zip
    Expand-Archive $zip -DestinationPath vendor -Force
}

.\.venv-win\Scripts\python packaging\render_icons.py
.\.venv-win\Scripts\python -m pytest -q tests
.\.venv-win\Scripts\pyinstaller --noconfirm --clean --distpath dist --workpath build\pyinstaller packaging\freedom.spec

$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { $iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" }
if (-not (Test-Path $iscc)) {
    winget install --id JRSoftware.InnoSetup -e --accept-source-agreements --accept-package-agreements
    $iscc = (Get-ChildItem "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}
& $iscc "/DAppVersion=$version" packaging\windows\installer.iss
Write-Host "Installer: dist\Freedom-$version-windows-x64-setup.exe"
