# Windows Desktop Startup Script for Virtual Desktop Environment

Write-Host "Starting Autohire Windows Virtual Desktop Environment..." -ForegroundColor Green

# Set default values if not provided via environment variables
$VncPort = if ($env:VNC_PORT) { $env:VNC_PORT } else { "5901" }
$NoVncPort = if ($env:NOVNC_PORT) { $env:NOVNC_PORT } else { "6080" }
$Resolution = if ($env:VNC_RESOLUTION) { $env:VNC_RESOLUTION } else { "1920x1080" }

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  VNC Port: $VncPort"
Write-Host "  NoVNC Port: $NoVncPort"
Write-Host "  Resolution: $Resolution"

# Function to handle cleanup on exit
function Cleanup {
    Write-Host "Shutting down Windows Virtual Desktop Environment..." -ForegroundColor Yellow
    
    # Stop VNC Server
    try {
        Stop-Service -Name "TigerVNCServer" -Force -ErrorAction SilentlyContinue
        Write-Host "VNC Server stopped"
    } catch {
        Write-Host "Error stopping VNC Server: $_" -ForegroundColor Red
    }
    
    # Stop Remote Desktop Services
    try {
        Stop-Service -Name "TermService" -Force -ErrorAction SilentlyContinue
        Write-Host "Remote Desktop Services stopped"
    } catch {
        Write-Host "Error stopping Remote Desktop Services: $_" -ForegroundColor Red
    }
    
    Write-Host "Cleanup completed" -ForegroundColor Green
    exit 0
}

# Set up signal handlers (best effort in PowerShell)
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup }

try {
    # Configure Remote Desktop Services
    Write-Host "Configuring Remote Desktop Services..." -ForegroundColor Cyan
    
    # Enable Remote Desktop
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0
    
    # Configure RDP settings
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'UserAuthentication' -Value 0
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'PortNumber' -Value 3389
    
    # Configure display settings
    $resolutionParts = $Resolution -split 'x'
    if ($resolutionParts.Count -eq 2) {
        $width = [int]$resolutionParts[0]
        $height = [int]$resolutionParts[1]
        
        # Set display resolution registry settings
        Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'DefaultDesktopWidth' -Value $width
        Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'DefaultDesktopHeight' -Value $height
    }
    
    # Start Remote Desktop Services
    Write-Host "Starting Remote Desktop Services..." -ForegroundColor Cyan
    Start-Service -Name "TermService"
    Start-Service -Name "UmRdpService" -ErrorAction SilentlyContinue
    
    # Wait for services to start
    $timeout = 30
    $elapsed = 0
    while ((Get-Service "TermService").Status -ne "Running" -and $elapsed -lt $timeout) {
        Start-Sleep -Seconds 1
        $elapsed++
    }
    
    if ((Get-Service "TermService").Status -eq "Running") {
        Write-Host "Remote Desktop Services started successfully" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Remote Desktop Services failed to start within $timeout seconds" -ForegroundColor Yellow
    }
    
    # Configure firewall rules
    Write-Host "Configuring Windows Firewall..." -ForegroundColor Cyan
    try {
        Enable-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "VNC Server" -Direction Inbound -Protocol TCP -LocalPort $VncPort -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "NoVNC Web Client" -Direction Inbound -Protocol TCP -LocalPort $NoVncPort -Action Allow -ErrorAction SilentlyContinue
        Write-Host "Firewall rules configured"
    } catch {
        Write-Host "Warning: Could not configure firewall rules: $_" -ForegroundColor Yellow
    }
    
    # Configure TigerVNC Server if available
    $vncExe = "C:\Program Files\TigerVNC\winvnc4.exe"
    if (Test-Path $vncExe) {
        Write-Host "Configuring TigerVNC Server..." -ForegroundColor Cyan
        
        # Create VNC configuration
        $vncConfigDir = "C:\Users\desktop\AppData\Roaming\TigerVNC"
        if (!(Test-Path $vncConfigDir)) {
            New-Item -Path $vncConfigDir -ItemType Directory -Force
        }
        
        # Set VNC password
        $vncPasswd = "$vncConfigDir\passwd"
        "desktop" | Out-File -FilePath $vncPasswd -Encoding ASCII -NoNewline
        
        # Start VNC Server
        try {
            Start-Service -Name "TigerVNCServer"
            Write-Host "TigerVNC Server started on port $VncPort" -ForegroundColor Green
        } catch {
            Write-Host "Could not start TigerVNC Server: $_" -ForegroundColor Yellow
            
            # Try to start manually
            try {
                Start-Process -FilePath $vncExe -ArgumentList "-rfbport $VncPort", "-rfbauth $vncPasswd" -WindowStyle Hidden
                Write-Host "TigerVNC Server started manually" -ForegroundColor Green
            } catch {
                Write-Host "Failed to start VNC Server manually: $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "TigerVNC Server not found, using Remote Desktop only" -ForegroundColor Yellow
    }
    
    # Install and configure noVNC web client
    Write-Host "Setting up noVNC web client..." -ForegroundColor Cyan
    try {
        $noVncPath = "C:\novnc"
        if (!(Test-Path $noVncPath)) {
            # Download noVNC
            $noVncZip = "C:\temp\novnc.zip"
            Invoke-WebRequest -Uri "https://github.com/novnc/noVNC/archive/refs/tags/v1.4.0.zip" -OutFile $noVncZip -UseBasicParsing
            
            # Extract noVNC
            Expand-Archive -Path $noVncZip -DestinationPath "C:\temp\"
            Move-Item -Path "C:\temp\noVNC-1.4.0" -Destination $noVncPath
            Remove-Item $noVncZip -Force
        }
        
        # Start noVNC web server (simplified Python server)
        $pythonExe = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonExe) {
            Start-Process -FilePath $pythonExe.Source -ArgumentList "-m", "http.server", $NoVncPort -WorkingDirectory $noVncPath -WindowStyle Hidden
            Write-Host "noVNC web client started on port $NoVncPort" -ForegroundColor Green
        } else {
            Write-Host "Python not found, noVNC web client not available" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Error setting up noVNC: $_" -ForegroundColor Red
    }
    
    # Configure desktop environment
    Write-Host "Configuring desktop environment..." -ForegroundColor Cyan
    & "C:\scripts\configure-desktop.ps1"
    
    Write-Host "Windows Virtual Desktop Environment started successfully!" -ForegroundColor Green
    Write-Host "Access Methods:" -ForegroundColor Yellow
    Write-Host "  Remote Desktop (RDP): localhost:3389 (desktop/desktop)"
    Write-Host "  VNC: localhost:$VncPort (password: desktop)"
    Write-Host "  noVNC Web: http://localhost:$NoVncPort"
    
    # Keep the script running and monitor services
    Write-Host "Monitoring services..." -ForegroundColor Cyan
    while ($true) {
        # Check Remote Desktop Service
        $rdpService = Get-Service "TermService" -ErrorAction SilentlyContinue
        if (!$rdpService -or $rdpService.Status -ne "Running") {
            Write-Host "WARNING: Remote Desktop Service is not running, attempting to restart..." -ForegroundColor Yellow
            try {
                Start-Service -Name "TermService"
                Write-Host "Remote Desktop Service restarted successfully" -ForegroundColor Green
            } catch {
                Write-Host "ERROR: Failed to restart Remote Desktop Service: $_" -ForegroundColor Red
            }
        }
        
        # Check VNC Server if available
        $vncService = Get-Service "TigerVNCServer" -ErrorAction SilentlyContinue
        if ($vncService -and $vncService.Status -ne "Running") {
            Write-Host "WARNING: VNC Server is not running, attempting to restart..." -ForegroundColor Yellow
            try {
                Start-Service -Name "TigerVNCServer"
                Write-Host "VNC Server restarted successfully" -ForegroundColor Green
            } catch {
                Write-Host "Could not restart VNC Server: $_" -ForegroundColor Yellow
            }
        }
        
        # Display status every 5 minutes
        $currentTime = Get-Date
        if ($currentTime.Minute % 5 -eq 0 -and $currentTime.Second -eq 0) {
            Write-Host "Status Check - RDP: $($rdpService.Status), VNC: $(if($vncService){$vncService.Status}else{'N/A'})" -ForegroundColor Cyan
        }
        
        Start-Sleep -Seconds 30
    }
    
} catch {
    Write-Host "Error in startup script: $_" -ForegroundColor Red
    Cleanup
    exit 1
}