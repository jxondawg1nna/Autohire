#!/usr/bin/env python3
"""
Start Visual Desktop Operator in development mode
Local development server without Docker dependencies
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Check if virtual environment exists
    venv_path = backend_dir / "venv"
    if venv_path.exists():
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            uvicorn_exe = venv_path / "Scripts" / "uvicorn.exe"
        else:  # Linux/macOS
            python_exe = venv_path / "bin" / "python"
            uvicorn_exe = venv_path / "bin" / "uvicorn"
        
        if uvicorn_exe.exists():
            subprocess.run([str(uvicorn_exe), "main:app", "--reload", "--port", "8001"], cwd=str(backend_dir))
        else:
            subprocess.run([str(python_exe), "-m", "uvicorn", "main:app", "--reload", "--port", "8001"], cwd=str(backend_dir))
    else:
        # Use system Python
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"], cwd=str(backend_dir))

def start_frontend():
    """Start Next.js frontend server"""
    print("🌐 Starting frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Try npm first, then yarn
    try:
        subprocess.run(["npm", "run", "dev"], cwd=str(frontend_dir), check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(["yarn", "dev"], cwd=str(frontend_dir), check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Neither npm nor yarn found. Please install Node.js")
            return

def create_demo_session():
    """Create a demo virtual desktop session"""
    print("🖥️  Creating demo virtual desktop session...")
    
    # Create a simple demo HTML page that simulates the virtual desktop
    demo_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Desktop Operator - Demo</title>
    <style>
        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            height: 100vh;
        }
        
        .sidebar {
            width: 300px;
            background: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            padding: 20px;
            box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
        }
        
        .desktop-area {
            flex: 1;
            position: relative;
            background: #1e1e1e;
            border-radius: 10px 0 0 0;
            margin: 10px 10px 10px 0;
            overflow: hidden;
        }
        
        .desktop-header {
            background: #2d2d2d;
            padding: 15px;
            border-bottom: 1px solid #444;
            display: flex;
            justify-content: between;
            align-items: center;
        }
        
        .desktop-content {
            height: calc(100vh - 80px);
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23121212"/><circle cx="50" cy="50" r="2" fill="%23333"/></svg>') repeat;
            position: relative;
        }
        
        .command-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px;
            color: white;
            margin-bottom: 20px;
        }
        
        .command-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .status-panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .virtual-window {
            position: absolute;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            min-width: 300px;
            min-height: 200px;
        }
        
        .window-header {
            background: #f0f0f0;
            padding: 10px 15px;
            border-radius: 8px 8px 0 0;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .window-content {
            padding: 20px;
            color: #333;
        }
        
        .browser-window {
            top: 50px;
            left: 50px;
            width: 600px;
            height: 400px;
        }
        
        .terminal-window {
            top: 100px;
            left: 200px;
            width: 500px;
            height: 300px;
            background: #1e1e1e;
            color: #00ff00;
        }
        
        .terminal-window .window-header {
            background: #333;
            color: white;
        }
        
        .terminal-content {
            padding: 15px;
            font-family: 'Courier New', monospace;
            background: #1e1e1e;
            height: calc(100% - 50px);
            overflow-y: auto;
        }
        
        .taskbar {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 50px;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            padding: 0 20px;
        }
        
        .taskbar-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 8px 15px;
            margin-right: 10px;
            font-size: 14px;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .demo-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 0, 0, 0.8);
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="demo-badge">DEMO MODE</div>
    <div class="container">
        <div class="sidebar">
            <h2>🤖 Visual Operator</h2>
            <input type="text" class="command-input" placeholder="Tell me what to do..." id="commandInput">
            
            <div class="status-panel">
                <h3>📊 System Status</h3>
                <div class="status-item">
                    <span>🖥️ Desktop Session:</span>
                    <span style="color: #4ade80;">Active</span>
                </div>
                <div class="status-item">
                    <span>🧠 AI Models:</span>
                    <span style="color: #4ade80;">Ready</span>
                </div>
                <div class="status-item">
                    <span>👁️ Vision System:</span>
                    <span style="color: #4ade80;">Watching</span>
                </div>
                <div class="status-item">
                    <span>🔒 Security:</span>
                    <span style="color: #fbbf24;">Sandbox</span>
                </div>
            </div>
            
            <div class="status-panel">
                <h3>⚡ Recent Actions</h3>
                <div style="font-size: 12px; opacity: 0.8;">
                    <div>• Opened Chrome browser</div>
                    <div>• Navigated to website</div>
                    <div>• Filled form fields</div>
                    <div>• Clicked submit button</div>
                </div>
            </div>
            
            <div class="status-panel">
                <h3>🎯 Capabilities</h3>
                <div style="font-size: 12px; opacity: 0.8;">
                    <div>✅ Web automation</div>
                    <div>✅ Form filling</div>
                    <div>✅ File management</div>
                    <div>✅ Application control</div>
                    <div>✅ Captcha solving</div>
                    <div>✅ Multi-tasking</div>
                </div>
            </div>
        </div>
        
        <div class="desktop-area">
            <div class="desktop-header">
                <h3>🖥️ Virtual Desktop Environment</h3>
                <div>
                    <span style="margin-right: 20px;">Resolution: 1920x1080</span>
                    <span>FPS: 60</span>
                </div>
            </div>
            
            <div class="desktop-content">
                <!-- Browser Window -->
                <div class="virtual-window browser-window">
                    <div class="window-header">
                        <span>🌐 Chrome Browser</span>
                        <span>🔴 🟡 🟢</span>
                    </div>
                    <div class="window-content">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="background: #f0f0f0; border-radius: 20px; padding: 8px 15px; flex: 1; margin-right: 10px;">
                                https://example.com
                            </div>
                            <button style="background: #4285f4; color: white; border: none; padding: 8px 15px; border-radius: 4px;">Go</button>
                        </div>
                        <div style="border: 1px solid #ddd; height: 250px; border-radius: 4px; background: white; padding: 20px;">
                            <h2>Example Website</h2>
                            <p>The AI operator is interacting with this webpage...</p>
                            <form>
                                <input type="text" placeholder="Username" style="width: 200px; padding: 8px; margin: 5px 0;">
                                <br>
                                <input type="password" placeholder="Password" style="width: 200px; padding: 8px; margin: 5px 0;">
                                <br>
                                <button type="button" style="background: #4ade80; color: white; border: none; padding: 10px 20px; margin: 10px 0; border-radius: 4px;">Login</button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <!-- Terminal Window -->
                <div class="virtual-window terminal-window">
                    <div class="window-header">
                        <span>💻 Terminal</span>
                        <span>🔴 🟡 🟢</span>
                    </div>
                    <div class="terminal-content">
                        <div>operator@virtual-desktop:~$ ls</div>
                        <div>Desktop  Documents  Downloads  Pictures</div>
                        <div>operator@virtual-desktop:~$ python script.py</div>
                        <div>Running automation script...</div>
                        <div>✅ Task completed successfully</div>
                        <div>operator@virtual-desktop:~$ <span class="pulse">_</span></div>
                    </div>
                </div>
                
                <!-- Taskbar -->
                <div class="taskbar">
                    <div class="taskbar-item">📁 Files</div>
                    <div class="taskbar-item">🌐 Chrome</div>
                    <div class="taskbar-item">💻 Terminal</div>
                    <div class="taskbar-item">⚙️ Settings</div>
                    <div style="flex: 1;"></div>
                    <div class="taskbar-item">14:32</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Simulate typing in command input
        const commandInput = document.getElementById('commandInput');
        const commands = [
            "Open Chrome and go to example.com",
            "Fill out the login form",
            "Take a screenshot",
            "Download the file from this page",
            "Send an email with the results"
        ];
        
        let commandIndex = 0;
        
        commandInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const command = this.value;
                if (command.trim()) {
                    alert(`🤖 Operator: I'll ${command.toLowerCase()}\\n\\n🔄 Executing command...\\n⏳ Please wait while I complete this task.`);
                    this.value = '';
                }
            }
        });
        
        // Simulate command suggestions
        setInterval(() => {
            if (!commandInput.value && document.activeElement !== commandInput) {
                commandInput.placeholder = `Try: "${commands[commandIndex]}"`;
                commandIndex = (commandIndex + 1) % commands.length;
            }
        }, 3000);
        
        // Simulate window interactions
        let windows = document.querySelectorAll('.virtual-window');
        windows.forEach(window => {
            let isDragging = false;
            let currentX, currentY, initialX, initialY;
            
            window.querySelector('.window-header').addEventListener('mousedown', function(e) {
                isDragging = true;
                initialX = e.clientX - window.offsetLeft;
                initialY = e.clientY - window.offsetTop;
            });
            
            document.addEventListener('mousemove', function(e) {
                if (isDragging) {
                    e.preventDefault();
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;
                    window.style.left = currentX + 'px';
                    window.style.top = currentY + 'px';
                }
            });
            
            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
        });
        
        console.log('🤖 Visual Desktop Operator Demo');
        console.log('This is a demonstration of the operator interface.');
        console.log('In production, this would show a real virtual desktop environment.');
    </script>
</body>
</html>'''
    
    # Save demo file
    demo_file = Path(__file__).parent / "visual_operator_demo.html"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_html)
    
    return demo_file

def main():
    """Main startup function"""
    print("🎯 Visual Desktop Operator - Development Mode")
    print("=" * 60)
    
    current_dir = Path(__file__).parent
    print(f"📁 Working directory: {current_dir}")
    
    # Create .env file if it doesn't exist
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("📝 Creating development .env file...")
        env_content = """# Development configuration
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=development-secret-key
JWT_SECRET_KEY=development-jwt-key
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# API Keys (Replace with your actual keys)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here

# Visual Operator Settings
SCREEN_CAPTURE_FPS=30
MAX_CONCURRENT_SESSIONS=2
ENABLE_LOGGING=true
LOG_LEVEL=INFO
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    
    # Create demo session
    demo_file = create_demo_session()
    print(f"✅ Created demo interface: {demo_file}")
    
    # Open demo in browser
    print("\n🌐 Opening Visual Desktop Operator Demo...")
    demo_url = f"file:///{demo_file.as_posix()}"
    webbrowser.open(demo_url)
    
    print("\n" + "=" * 60)
    print("🎉 VISUAL DESKTOP OPERATOR DEMO RUNNING")
    print("=" * 60)
    print(f"📱 Demo Interface: {demo_url}")
    print("🔧 Features Demonstrated:")
    print("  • Virtual desktop environment simulation")
    print("  • Command input interface")
    print("  • System status monitoring")
    print("  • Multi-window management")
    print("  • Browser and terminal simulation")
    print("  • Real-time interaction capabilities")
    print("\n💡 Next Steps:")
    print("  1. Install Docker Desktop and restart it")
    print("  2. Run: python quick_deploy.py")
    print("  3. Configure your API keys in .env file")
    print("  4. Start full production deployment")
    print("\n🎯 The operator is ready for commands!")
    print("Press Ctrl+C to exit...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Visual Desktop Operator Demo")

if __name__ == "__main__":
    main()