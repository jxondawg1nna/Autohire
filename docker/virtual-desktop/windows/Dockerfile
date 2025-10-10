# Windows Server Container for Virtual Desktop Environment
# escape=`
FROM mcr.microsoft.com/windows/servercore:ltsc2022

LABEL maintainer="Autohire Visual Operator Team" `
      description="Windows Desktop Environment for Virtual Desktop Operations"

# Set shell to PowerShell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Chocolatey package manager
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Desktop Experience and GUI components
RUN dism /online /enable-feature /featurename:ServerCore-FullServer-OOB-GUI /all; `
    dism /online /enable-feature /featurename:Server-Gui-Mgmt-Infra /all; `
    dism /online /enable-feature /featurename:Server-Gui-Shell /all

# Install Remote Desktop Services
RUN dism /online /enable-feature /featurename:Remote-Desktop-Services /all; `
    dism /online /enable-feature /featurename:RDS-RD-Server /all

# Install essential software via Chocolatey
RUN choco install -y `
    googlechrome `
    firefox `
    git `
    python3 `
    nodejs `
    vscode `
    notepadplusplus `
    7zip `
    putty `
    filezilla `
    vlc `
    --ignore-checksums

# Install .NET Framework and Visual C++ Redistributables
RUN choco install -y `
    dotnet-windowshosting `
    vcredist140 `
    vcredist2017 `
    --ignore-checksums

# Install TigerVNC Server for Windows
RUN Invoke-WebRequest -Uri 'https://bintray.com/tigervnc/stable/download_file?file_path=tigervnc64-1.12.0.exe' -OutFile 'C:\temp\tigervnc-installer.exe'; `
    Start-Process -FilePath 'C:\temp\tigervnc-installer.exe' -ArgumentList '/S' -Wait; `
    Remove-Item 'C:\temp\tigervnc-installer.exe' -Force

# Configure Remote Desktop
RUN Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0; `
    Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'; `
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'UserAuthentication' -Value 0

# Create desktop user
RUN net user desktop desktop /add; `
    net localgroup administrators desktop /add; `
    net localgroup "Remote Desktop Users" desktop /add

# Configure VNC Server
RUN mkdir C:\Users\desktop\AppData\Roaming\TigerVNC; `
    echo 'desktop' | Out-File -FilePath 'C:\Users\desktop\AppData\Roaming\TigerVNC\passwd' -Encoding ASCII

# Create startup scripts directory
RUN mkdir C:\scripts

# Copy startup scripts
COPY scripts\start-windows-desktop.ps1 C:\scripts\
COPY scripts\configure-desktop.ps1 C:\scripts\

# Set execution policy and make scripts executable
RUN Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force

# Create Windows service for VNC
RUN New-Service -Name 'TigerVNCServer' -BinaryPathName 'C:\Program Files\TigerVNC\winvnc4.exe -service' -DisplayName 'TigerVNC Server' -Description 'VNC Server for remote desktop access' -StartupType Manual

# Configure automatic logon for desktop user
RUN Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name 'AutoAdminLogon' -Value '1'; `
    Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name 'DefaultUserName' -Value 'desktop'; `
    Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name 'DefaultPassword' -Value 'desktop'

# Create desktop shortcuts
RUN $WshShell = New-Object -comObject WScript.Shell; `
    $Shortcut = $WshShell.CreateShortcut('C:\Users\Public\Desktop\Google Chrome.lnk'); `
    $Shortcut.TargetPath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'; `
    $Shortcut.Save(); `
    `
    $Shortcut = $WshShell.CreateShortcut('C:\Users\Public\Desktop\Firefox.lnk'); `
    $Shortcut.TargetPath = 'C:\Program Files\Mozilla Firefox\firefox.exe'; `
    $Shortcut.Save(); `
    `
    $Shortcut = $WshShell.CreateShortcut('C:\Users\Public\Desktop\Visual Studio Code.lnk'); `
    $Shortcut.TargetPath = 'C:\Program Files\Microsoft VS Code\Code.exe'; `
    $Shortcut.Save(); `
    `
    $Shortcut = $WshShell.CreateShortcut('C:\Users\Public\Desktop\Command Prompt.lnk'); `
    $Shortcut.TargetPath = 'C:\Windows\System32\cmd.exe'; `
    $Shortcut.Save(); `
    `
    $Shortcut = $WshShell.CreateShortcut('C:\Users\Public\Desktop\PowerShell.lnk'); `
    $Shortcut.TargetPath = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'; `
    $Shortcut.Save()

# Configure Windows services
RUN Set-Service -Name 'TermService' -StartupType Automatic; `
    Set-Service -Name 'UmRdpService' -StartupType Automatic

# Expose Remote Desktop and VNC ports
EXPOSE 3389 5901 6080

# Set working directory
WORKDIR C:\scripts

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 `
    CMD powershell -command "if ((Get-Service TermService).Status -eq 'Running') { exit 0 } else { exit 1 }"

# Set entrypoint
ENTRYPOINT ["powershell", "-File", "C:\\scripts\\start-windows-desktop.ps1"]

# Default command
CMD ["powershell", "-Command", "while ($true) { Start-Sleep -Seconds 30; Write-Host 'Windows Desktop Container Running...' }"]