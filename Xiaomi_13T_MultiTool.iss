[Setup]
AppName=Xiaomi 13T MultiTool 1.4
AppVersion=Turkey 1.4 
DefaultDirName={autopf}\Xiaomi 13T MultiTool
DefaultGroupName=Xiaomi 13T MultiTool
OutputDir=Setup
OutputBaseFilename=Xiaomi 13T MultiTool Turkey Build
Compression=lzma2/ultra64
SolidCompression=yes
LZMANumFastBytes=273
LZMAMatchFinder=BT
LZMAUseSeparateProcess=yes
LZMADictionarySize=524288
WizardStyle=modern
InternalCompressLevel=ultra64
CompressionThreads=16
PrivilegesRequired=admin
SetupIconFile=unnamed.ico

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "output\Xiaomi 13T Hype\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Xiaomi 13T MultiTool"; Filename: "{app}\Xiaomi_13T_MultiTool\Turkey Version\Xiaomi_13T_MultiTool.exe"; WorkingDir: "{app}\Xiaomi_13T_MultiTool\Turkey Version"
Name: "{group}\{cm:UninstallProgram,Xiaomi 13T MultiTool}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Xiaomi 13T MultiTool"; Filename: "{app}\Xiaomi_13T_MultiTool\Turkey Version\Xiaomi_13T_MultiTool.exe"; WorkingDir: "{app}\Xiaomi_13T_MultiTool\Turkey Version"; Tasks: desktopicon

[Run]
Filename: "{app}\Xiaomi_13T_MultiTool\Turkey Version\Xiaomi_13T_MultiTool.exe"; Description: "{cm:LaunchProgram,Xiaomi 13T MultiTool}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
