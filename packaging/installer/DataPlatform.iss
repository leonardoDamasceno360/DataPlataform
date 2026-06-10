#define MyAppName "Data Platform"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#ifndef ProjectRoot
  #define ProjectRoot "..\.."
#endif
#define MyAppPublisher "Internal Distribution"
#define MyAppExeName "DataPlatform.exe"
#define MySourceDir ProjectRoot + "\dist"
#define MyOutputDir ProjectRoot + "\dist\installer"

[Setup]
AppId={{7A94E9D9-22CE-41E3-A5A3-8F77A8A6A6F2}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Data Platform
DefaultGroupName=Data Platform
DisableProgramGroupPage=yes
OutputDir={#MyOutputDir}
OutputBaseFilename=DataPlatform-Setup-{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos:"

[Files]
Source: "{#MySourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Data Platform"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Data Platform"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir Data Platform"; Flags: nowait postinstall skipifsilent
