#!/usr/bin/env python3
"""
Visual Desktop Operator Installation Script
Automatically installs all required dependencies and tools
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualOperatorInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = sys.version_info
        self.install_log = []
        
        # Minimum requirements
        self.min_python_version = (3, 11)
        self.min_node_version = "18.0.0"
        
        # Installation paths
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        self.tools_dir = self.base_dir / "tools"
        
        # Create tools directory
        self.tools_dir.mkdir(exist_ok=True)

    def log_step(self, step: str, success: bool = True, details: str = ""):
        """Log installation step"""
        status = "✅" if success else "❌"
        message = f"{status} {step}"
        if details:
            message += f" - {details}"
        
        logger.info(message)
        self.install_log.append({
            "step": step,
            "success": success,
            "details": details,
            "timestamp": pd.Timestamp.now().isoformat() if 'pd' in globals() else "unknown"
        })

    def run_command(self, cmd: List[str], shell: bool = False, cwd: str = None) -> bool:
        """Run shell command and return success status"""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return True
            else:
                logger.error(f"Command failed: {' '.join(cmd)}")
                logger.error(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            return False
        except Exception as e:
            logger.error(f"Exception running command {' '.join(cmd)}: {e}")
            return False

    def check_python_version(self) -> bool:
        """Check Python version requirements"""
        if self.python_version >= self.min_python_version:
            self.log_step(f"Python version check", True, f"Python {sys.version}")
            return True
        else:
            self.log_step(
                f"Python version check", 
                False, 
                f"Found {sys.version}, need {self.min_python_version}+"
            )
            return False

    def install_system_dependencies(self) -> bool:
        """Install system-specific dependencies"""
        try:
            if self.system == "windows":
                return self._install_windows_dependencies()
            elif self.system == "linux":
                return self._install_linux_dependencies()
            elif self.system == "darwin":
                return self._install_macos_dependencies()
            else:
                self.log_step("System dependencies", False, f"Unsupported OS: {self.system}")
                return False
        except Exception as e:
            self.log_step("System dependencies", False, str(e))
            return False

    def _install_windows_dependencies(self) -> bool:
        """Install Windows-specific dependencies"""
        logger.info("Installing Windows dependencies...")
        
        # Check for chocolatey
        choco_installed = self.run_command(["choco", "--version"])
        if not choco_installed:
            logger.info("Installing Chocolatey package manager...")
            powershell_cmd = [
                "powershell",
                "-Command",
                "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
            ]
            if not self.run_command(powershell_cmd, shell=True):
                self.log_step("Chocolatey installation", False)
                return False
        
        # Install required packages via chocolatey
        packages = [
            "git",
            "nodejs",
            "python311",
            "postgresql15",
            "redis-64",
            "googlechrome",
            "firefox",
            "ffmpeg",
            "cmake",
            "vcredist2019"
        ]
        
        for package in packages:
            if self.run_command(["choco", "install", package, "-y"]):
                self.log_step(f"Install {package}", True)
            else:
                self.log_step(f"Install {package}", False)
        
        # Install Visual Studio Build Tools
        logger.info("Installing Visual Studio Build Tools...")
        vs_installer_url = "https://aka.ms/vs/17/release/vs_buildtools.exe"
        vs_installer_path = self.tools_dir / "vs_buildtools.exe"
        
        try:
            urllib.request.urlretrieve(vs_installer_url, vs_installer_path)
            vs_cmd = [
                str(vs_installer_path),
                "--quiet",
                "--wait",
                "--add", "Microsoft.VisualStudio.Workload.VCTools",
                "--add", "Microsoft.VisualStudio.Component.Windows10SDK.19041"
            ]
            if self.run_command(vs_cmd):
                self.log_step("Visual Studio Build Tools", True)
            else:
                self.log_step("Visual Studio Build Tools", False)
        except Exception as e:
            self.log_step("Visual Studio Build Tools", False, str(e))
        
        return True

    def _install_linux_dependencies(self) -> bool:
        """Install Linux-specific dependencies"""
        logger.info("Installing Linux dependencies...")
        
        # Update package list
        if not self.run_command(["sudo", "apt-get", "update"]):
            self.log_step("Package update", False)
            return False
        
        # Install system packages
        packages = [
            "python3-dev", "python3-pip", "python3-venv",
            "build-essential", "cmake", "pkg-config",
            "libjpeg-dev", "libtiff5-dev", "libpng-dev",
            "libavcodec-dev", "libavformat-dev", "libswscale-dev",
            "libv4l-dev", "libxvidcore-dev", "libx264-dev",
            "libgtk-3-dev", "libatlas-base-dev", "gfortran",
            "libgstreamer1.0-dev", "libgstreamer-plugins-base1.0-dev",
            "ffmpeg", "tesseract-ocr", "libtesseract-dev",
            "xvfb", "x11vnc", "fluxbox",
            "nodejs", "npm", "postgresql", "redis-server",
            "google-chrome-stable", "firefox"
        ]
        
        # Add Google Chrome repository
        chrome_cmds = [
            ["wget", "-q", "-O", "-", "https://dl.google.com/linux/linux_signing_key.pub"],
            ["sudo", "apt-key", "add", "-"],
            ["sudo", "sh", "-c", "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"],
            ["sudo", "apt-get", "update"]
        ]
        
        for cmd in chrome_cmds:
            self.run_command(cmd)
        
        # Install all packages
        install_cmd = ["sudo", "apt-get", "install", "-y"] + packages
        if self.run_command(install_cmd):
            self.log_step("Linux system packages", True)
        else:
            self.log_step("Linux system packages", False)
            return False
        
        return True

    def _install_macos_dependencies(self) -> bool:
        """Install macOS-specific dependencies"""
        logger.info("Installing macOS dependencies...")
        
        # Check for Homebrew
        brew_installed = self.run_command(["brew", "--version"])
        if not brew_installed:
            logger.info("Installing Homebrew...")
            brew_install_cmd = [
                "/bin/bash", "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            ]
            if not self.run_command(brew_install_cmd):
                self.log_step("Homebrew installation", False)
                return False
        
        # Install packages via Homebrew
        packages = [
            "python@3.11", "node", "postgresql@15", "redis",
            "opencv", "tesseract", "ffmpeg", "cmake", "pkg-config",
            "jpeg", "libpng", "libtiff", "openexr", "eigen", "tbb"
        ]
        
        for package in packages:
            if self.run_command(["brew", "install", package]):
                self.log_step(f"Install {package}", True)
            else:
                self.log_step(f"Install {package}", False)
        
        # Install Cask packages
        cask_packages = ["google-chrome", "firefox"]
        for package in cask_packages:
            if self.run_command(["brew", "install", "--cask", package]):
                self.log_step(f"Install {package}", True)
            else:
                self.log_step(f"Install {package}", False)
        
        return True

    def setup_python_environment(self) -> bool:
        """Setup Python virtual environment and install packages"""
        try:
            logger.info("Setting up Python environment...")
            
            # Create virtual environment
            venv_path = self.backend_dir / "venv"
            if not venv_path.exists():
                if not self.run_command([sys.executable, "-m", "venv", str(venv_path)]):
                    self.log_step("Create virtual environment", False)
                    return False
            
            # Determine activation script
            if self.system == "windows":
                pip_path = venv_path / "Scripts" / "pip.exe"
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
            
            # Upgrade pip
            if self.run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"]):
                self.log_step("Upgrade pip", True)
            else:
                self.log_step("Upgrade pip", False)
            
            # Install requirements
            requirements_file = self.backend_dir / "requirements.txt"
            if requirements_file.exists():
                if self.run_command([str(pip_path), "install", "-r", str(requirements_file)]):
                    self.log_step("Install Python packages", True)
                else:
                    self.log_step("Install Python packages", False)
                    return False
            
            # Install additional packages
            additional_packages = [
                "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121"
            ]
            if self.run_command([str(pip_path), "install"] + additional_packages):
                self.log_step("Install PyTorch with CUDA", True)
            else:
                self.log_step("Install PyTorch with CUDA", False, "Will use CPU version")
            
            # Download NLTK and spaCy data
            nltk_cmd = [str(python_path), "-c", "import nltk; nltk.download('all')"]
            if self.run_command(nltk_cmd):
                self.log_step("Download NLTK data", True)
            
            spacy_cmd = [str(python_path), "-m", "spacy", "download", "en_core_web_sm"]
            if self.run_command(spacy_cmd):
                self.log_step("Download spaCy model", True)
            
            return True
            
        except Exception as e:
            self.log_step("Python environment setup", False, str(e))
            return False

    def setup_frontend_environment(self) -> bool:
        """Setup Node.js environment and install packages"""
        try:
            logger.info("Setting up frontend environment...")
            
            # Check Node.js version
            if not self.run_command(["node", "--version"]):
                self.log_step("Node.js check", False, "Node.js not found")
                return False
            
            # Install frontend dependencies
            if self.run_command(["npm", "install"], cwd=str(self.frontend_dir)):
                self.log_step("Install frontend packages", True)
            else:
                self.log_step("Install frontend packages", False)
                return False
            
            # Install global packages
            global_packages = ["typescript", "create-next-app", "@next/bundle-analyzer"]
            for package in global_packages:
                if self.run_command(["npm", "install", "-g", package]):
                    self.log_step(f"Install global {package}", True)
                else:
                    self.log_step(f"Install global {package}", False)
            
            return True
            
        except Exception as e:
            self.log_step("Frontend environment setup", False, str(e))
            return False

    def setup_browsers_and_drivers(self) -> bool:
        """Setup browsers and WebDriver binaries"""
        try:
            logger.info("Setting up browsers and drivers...")
            
            # Get Python path from virtual environment
            if self.system == "windows":
                python_path = self.backend_dir / "venv" / "Scripts" / "python.exe"
            else:
                python_path = self.backend_dir / "venv" / "bin" / "python"
            
            # Install Playwright browsers
            playwright_cmds = [
                [str(python_path), "-m", "playwright", "install"],
                [str(python_path), "-m", "playwright", "install-deps"]
            ]
            
            for cmd in playwright_cmds:
                if self.run_command(cmd):
                    self.log_step("Playwright browser setup", True)
                else:
                    self.log_step("Playwright browser setup", False)
            
            # Verify Chrome installation
            chrome_paths = {
                "windows": [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                ],
                "linux": ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"],
                "darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
            }
            
            chrome_found = False
            for path in chrome_paths.get(self.system, []):
                if Path(path).exists():
                    chrome_found = True
                    break
            
            if chrome_found:
                self.log_step("Chrome browser", True)
            else:
                self.log_step("Chrome browser", False, "Chrome not found")
            
            return True
            
        except Exception as e:
            self.log_step("Browser setup", False, str(e))
            return False

    def setup_database_services(self) -> bool:
        """Setup PostgreSQL and Redis"""
        try:
            logger.info("Setting up database services...")
            
            # Check PostgreSQL
            if self.run_command(["pg_config", "--version"]):
                self.log_step("PostgreSQL check", True)
                
                # Create database
                if self.run_command(["createdb", "autohire_visual_operator"]):
                    self.log_step("Create database", True)
                else:
                    self.log_step("Create database", False, "Database may already exist")
            else:
                self.log_step("PostgreSQL check", False)
            
            # Check Redis
            if self.run_command(["redis-cli", "ping"]):
                self.log_step("Redis check", True)
            else:
                self.log_step("Redis check", False, "Redis may not be running")
            
            return True
            
        except Exception as e:
            self.log_step("Database setup", False, str(e))
            return False

    def create_environment_file(self) -> bool:
        """Create .env file with default configuration"""
        try:
            logger.info("Creating environment configuration...")
            
            env_content = '''# Visual Desktop Operator Configuration

# API Keys (Required - Replace with your actual keys)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here

# Captcha Solving Services (Optional - Choose one)
TWOCAPTCHA_API_KEY=your-2captcha-key
ANTICAPTCHA_API_KEY=your-anticaptcha-key
CAPMONSTER_API_KEY=your-capmonster-key

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/autohire_visual_operator
REDIS_URL=redis://localhost:6379/0

# Security Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Visual Operator Settings
SCREEN_CAPTURE_FPS=30
MAX_CONCURRENT_SESSIONS=3
SESSION_TIMEOUT=3600
ENABLE_LOGGING=true
LOG_LEVEL=INFO

# Anti-Detection Settings
USE_PROXIES=false
PROXY_LIST=[]
RESIDENTIAL_PROXY_ENDPOINT=""
ENABLE_BROWSER_ROTATION=true
HUMAN_BEHAVIOR_SIMULATION=true

# Performance Settings
MAX_MEMORY_USAGE_MB=8192
GPU_MEMORY_FRACTION=0.7
ENABLE_CUDA=true
BATCH_SIZE=4

# Safety Settings
ENABLE_CONTENT_FILTER=true
BLOCK_DANGEROUS_COMMANDS=true
REQUIRE_CONFIRMATION=false
AUDIT_ALL_ACTIONS=true

# Development Settings
DEBUG=true
ENVIRONMENT=development
ENABLE_HOT_RELOAD=true
'''
            
            env_file = self.base_dir / ".env"
            if not env_file.exists():
                with open(env_file, 'w') as f:
                    f.write(env_content)
                self.log_step("Create .env file", True)
            else:
                self.log_step("Create .env file", False, ".env already exists")
            
            return True
            
        except Exception as e:
            self.log_step("Environment file creation", False, str(e))
            return False

    def run_verification_tests(self) -> bool:
        """Run verification tests to ensure everything is working"""
        try:
            logger.info("Running verification tests...")
            
            # Get Python path from virtual environment
            if self.system == "windows":
                python_path = self.backend_dir / "venv" / "Scripts" / "python.exe"
            else:
                python_path = self.backend_dir / "venv" / "bin" / "python"
            
            # Test script content
            test_script = '''
import sys
print("Testing core dependencies...")

try:
    import cv2
    print("✅ OpenCV:", cv2.__version__)
except ImportError as e:
    print("❌ OpenCV:", e)

try:
    import numpy as np
    print("✅ NumPy:", np.__version__)
except ImportError as e:
    print("❌ NumPy:", e)

try:
    import pyautogui
    print("✅ PyAutoGUI:", pyautogui.__version__)
except ImportError as e:
    print("❌ PyAutoGUI:", e)

try:
    import selenium
    print("✅ Selenium:", selenium.__version__)
except ImportError as e:
    print("❌ Selenium:", e)

try:
    import openai
    print("✅ OpenAI:", openai.__version__)
except ImportError as e:
    print("❌ OpenAI:", e)

try:
    import anthropic
    print("✅ Anthropic:", anthropic.__version__)
except ImportError as e:
    print("❌ Anthropic:", e)

try:
    from ultralytics import YOLO
    print("✅ YOLO/Ultralytics: Available")
except ImportError as e:
    print("❌ YOLO/Ultralytics:", e)

try:
    import torch
    print("✅ PyTorch:", torch.__version__)
    print("✅ CUDA Available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("✅ GPU Device:", torch.cuda.get_device_name(0))
except ImportError as e:
    print("❌ PyTorch:", e)

print("\\nVerification complete!")
'''
            
            # Write and run test script
            test_file = self.backend_dir / "test_installation.py"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            if self.run_command([str(python_path), str(test_file)]):
                self.log_step("Verification tests", True)
            else:
                self.log_step("Verification tests", False)
            
            # Clean up test file
            test_file.unlink()
            
            return True
            
        except Exception as e:
            self.log_step("Verification tests", False, str(e))
            return False

    def generate_installation_report(self) -> None:
        """Generate installation report"""
        logger.info("Generating installation report...")
        
        report = {
            "system_info": {
                "os": self.system,
                "architecture": self.arch,
                "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}"
            },
            "installation_log": self.install_log,
            "summary": {
                "total_steps": len(self.install_log),
                "successful_steps": sum(1 for step in self.install_log if step["success"]),
                "failed_steps": sum(1 for step in self.install_log if not step["success"])
            }
        }
        
        # Write report
        report_file = self.base_dir / "installation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 VISUAL DESKTOP OPERATOR INSTALLATION COMPLETE")
        print("="*60)
        print(f"📊 Total Steps: {report['summary']['total_steps']}")
        print(f"✅ Successful: {report['summary']['successful_steps']}")
        print(f"❌ Failed: {report['summary']['failed_steps']}")
        
        if report['summary']['failed_steps'] > 0:
            print("\n⚠️  Some steps failed. Check the installation report for details.")
            print(f"📄 Report saved to: {report_file}")
        else:
            print("\n🎉 All components installed successfully!")
        
        print("\n📋 Next Steps:")
        print("1. Edit the .env file with your API keys")
        print("2. Start the services: docker-compose -f docker-compose.visual-operator.yml up -d")
        print("3. Access the dashboard at: http://localhost:3000")
        print("4. Read the documentation: VISUAL_OPERATOR_REQUIREMENTS.md")
        
        print(f"\n💾 Installation report saved to: {report_file}")

    def install(self) -> bool:
        """Run complete installation process"""
        logger.info("Starting Visual Desktop Operator installation...")
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        # Installation steps
        steps = [
            ("System Dependencies", self.install_system_dependencies),
            ("Python Environment", self.setup_python_environment),
            ("Frontend Environment", self.setup_frontend_environment),
            ("Browsers and Drivers", self.setup_browsers_and_drivers),
            ("Database Services", self.setup_database_services),
            ("Environment Configuration", self.create_environment_file),
            ("Verification Tests", self.run_verification_tests),
        ]
        
        for step_name, step_function in steps:
            logger.info(f"Running step: {step_name}")
            try:
                if not step_function():
                    logger.error(f"Step failed: {step_name}")
                    # Continue with other steps even if one fails
            except Exception as e:
                logger.error(f"Exception in step {step_name}: {e}")
        
        # Generate report
        self.generate_installation_report()
        
        return True

def main():
    """Main installation function"""
    installer = VisualOperatorInstaller()
    installer.install()

if __name__ == "__main__":
    main()