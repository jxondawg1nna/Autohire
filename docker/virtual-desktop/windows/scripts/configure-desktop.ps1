# Desktop Environment Configuration Script

Write-Host "Configuring Windows Desktop Environment..." -ForegroundColor Cyan

try {
    # Set desktop wallpaper to solid color for better VNC performance
    Write-Host "Setting desktop wallpaper..." -ForegroundColor Gray
    $wallpaperPath = "C:\Windows\Web\Wallpaper\Windows\img0.jpg"
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "Wallpaper" -Value $wallpaperPath -ErrorAction SilentlyContinue
    
    # Disable visual effects for better performance
    Write-Host "Optimizing visual effects..." -ForegroundColor Gray
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -ErrorAction SilentlyContinue
    
    # Configure taskbar
    Write-Host "Configuring taskbar..." -ForegroundColor Gray
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -Value 0 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarGlomLevel" -Value 1 -ErrorAction SilentlyContinue
    
    # Pin applications to taskbar
    Write-Host "Configuring application shortcuts..." -ForegroundColor Gray
    
    # Create taskbar shortcuts using COM object
    $shell = New-Object -ComObject Shell.Application
    
    # Pin Google Chrome to taskbar
    $chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    if (Test-Path $chromeExe) {
        $folder = $shell.Namespace((Split-Path $chromeExe))
        $item = $folder.ParseName((Split-Path $chromeExe -Leaf))
        $item.InvokeVerb("taskbarpin") -ErrorAction SilentlyContinue
    }
    
    # Pin Firefox to taskbar
    $firefoxExe = "C:\Program Files\Mozilla Firefox\firefox.exe"
    if (Test-Path $firefoxExe) {
        $folder = $shell.Namespace((Split-Path $firefoxExe))
        $item = $folder.ParseName((Split-Path $firefoxExe -Leaf))
        $item.InvokeVerb("taskbarpin") -ErrorAction SilentlyContinue
    }
    
    # Pin VS Code to taskbar
    $vscodeExe = "C:\Program Files\Microsoft VS Code\Code.exe"
    if (Test-Path $vscodeExe) {
        $folder = $shell.Namespace((Split-Path $vscodeExe))
        $item = $folder.ParseName((Split-Path $vscodeExe -Leaf))
        $item.InvokeVerb("taskbarpin") -ErrorAction SilentlyContinue
    }
    
    # Configure Windows Explorer
    Write-Host "Configuring Windows Explorer..." -ForegroundColor Gray
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "Hidden" -Value 1 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value 0 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowSuperHidden" -Value 1 -ErrorAction SilentlyContinue
    
    # Disable Windows Defender real-time protection for better performance
    Write-Host "Configuring Windows Defender..." -ForegroundColor Gray
    try {
        Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Could not disable Windows Defender real-time protection" -ForegroundColor Yellow
    }
    
    # Configure power settings
    Write-Host "Configuring power settings..." -ForegroundColor Gray
    powercfg.exe /change standby-timeout-ac 0
    powercfg.exe /change standby-timeout-dc 0
    powercfg.exe /change monitor-timeout-ac 0
    powercfg.exe /change monitor-timeout-dc 0
    powercfg.exe /change hibernate-timeout-ac 0
    powercfg.exe /change hibernate-timeout-dc 0
    
    # Disable Windows Update automatic restart
    Write-Host "Configuring Windows Update..." -ForegroundColor Gray
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" -Name "UxOption" -Value 1 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "NoAutoRebootWithLoggedOnUsers" -Value 1 -ErrorAction SilentlyContinue
    
    # Configure time zone
    Write-Host "Setting time zone..." -ForegroundColor Gray
    tzutil.exe /s "UTC"
    
    # Create desktop shortcuts for common tools
    Write-Host "Creating additional desktop shortcuts..." -ForegroundColor Gray
    $WshShell = New-Object -comObject WScript.Shell
    
    # Create shortcuts for development tools
    if (Test-Path "C:\Program Files\Git\bin\bash.exe") {
        $Shortcut = $WshShell.CreateShortcut("C:\Users\Public\Desktop\Git Bash.lnk")
        $Shortcut.TargetPath = "C:\Program Files\Git\bin\bash.exe"
        $Shortcut.WorkingDirectory = "C:\Users\desktop"
        $Shortcut.Save()
    }
    
    if (Test-Path "C:\Program Files\Notepad++\notepad++.exe") {
        $Shortcut = $WshShell.CreateShortcut("C:\Users\Public\Desktop\Notepad++.lnk")
        $Shortcut.TargetPath = "C:\Program Files\Notepad++\notepad++.exe"
        $Shortcut.Save()
    }
    
    # Create folder shortcuts
    $Shortcut = $WshShell.CreateShortcut("C:\Users\Public\Desktop\Desktop Folder.lnk")
    $Shortcut.TargetPath = "C:\Users\desktop\Desktop"
    $Shortcut.Save()
    
    $Shortcut = $WshShell.CreateShortcut("C:\Users\Public\Desktop\Documents.lnk")
    $Shortcut.TargetPath = "C:\Users\desktop\Documents"
    $Shortcut.Save()
    
    $Shortcut = $WshShell.CreateShortcut("C:\Users\Public\Desktop\Downloads.lnk")
    $Shortcut.TargetPath = "C:\Users\desktop\Downloads"
    $Shortcut.Save()
    
    # Configure Chrome for automation
    Write-Host "Configuring Chrome for automation..." -ForegroundColor Gray
    $chromePrefs = @"
{
   "browser": {
      "check_default_browser": false,
      "show_home_button": true
   },
   "distribution": {
      "import_bookmarks": false,
      "import_history": false,
      "import_search_engine": false,
      "make_chrome_default": false,
      "make_chrome_default_for_user": false,
      "verbose_logging": true
   },
   "first_run_tabs": [
      "about:blank"
   ],
   "homepage": "about:blank",
   "homepage_is_newtabpage": false,
   "profile": {
      "default_content_setting_values": {
         "notifications": 2,
         "geolocation": 2
      },
      "default_content_settings": {
         "popups": 0
      }
   }
}
"@
    
    $chromeUserData = "C:\Users\desktop\AppData\Local\Google\Chrome\User Data\Default"
    if (!(Test-Path $chromeUserData)) {
        New-Item -Path $chromeUserData -ItemType Directory -Force
    }
    $chromePrefs | Out-File -FilePath "$chromeUserData\Preferences" -Encoding UTF8
    
    # Configure Firefox for automation
    Write-Host "Configuring Firefox for automation..." -ForegroundColor Gray
    $firefoxProfile = "C:\Users\desktop\AppData\Roaming\Mozilla\Firefox\Profiles\default"
    if (!(Test-Path $firefoxProfile)) {
        New-Item -Path $firefoxProfile -ItemType Directory -Force
    }
    
    $firefoxPrefs = @"
user_pref("browser.startup.homepage", "about:blank");
user_pref("browser.startup.page", 0);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.tabs.warnOnClose", false);
user_pref("browser.sessionstore.resume_from_crash", false);
user_pref("dom.webnotifications.enabled", false);
user_pref("geo.enabled", false);
"@
    
    $firefoxPrefs | Out-File -FilePath "$firefoxProfile\prefs.js" -Encoding UTF8
    
    # Create batch files for common operations
    Write-Host "Creating utility scripts..." -ForegroundColor Gray
    
    # Script to restart desktop services
    $restartScript = @"
@echo off
echo Restarting desktop services...
net stop TermService
net start TermService
echo Desktop services restarted.
pause
"@
    $restartScript | Out-File -FilePath "C:\Users\Public\Desktop\Restart-Desktop-Services.bat" -Encoding ASCII
    
    # Script to open development tools
    $devScript = @"
@echo off
start "" "C:\Program Files\Microsoft VS Code\Code.exe"
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --new-window
start "" "C:\Windows\System32\cmd.exe"
echo Development environment launched.
"@
    $devScript | Out-File -FilePath "C:\Users\Public\Desktop\Launch-Dev-Environment.bat" -Encoding ASCII
    
    Write-Host "Desktop environment configuration completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "Error configuring desktop environment: $_" -ForegroundColor Red
}