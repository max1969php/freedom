; Installer Windows 10/11 (Inno Setup 6). Compilato da packaging/windows/build.ps1.
#define AppName "Freedom"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{6F0C3B7E-2E8B-4C5B-9C41-5A3F1D7E9B21}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Freedom
AppPublisherURL=https://github.com/max1969php/freedom
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; Senza diritti di amministratore si installa per l'utente corrente.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
OutputDir=..\..\dist
OutputBaseFilename=Freedom-{#AppVersion}-windows-x64-setup
SetupIconFile=..\..\build\icons\freedom.ico
UninstallDisplayIcon={app}\Freedom.exe
LicenseFile=..\..\..\LICENSE
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\..\dist\freedom\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Freedom.exe"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Freedom.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Freedom.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Il motore yt-dlp aggiornato dall'app (non i file scaricati, che restano dove sono).
Type: filesandordirs; Name: "{localappdata}\Freedom\engine"
