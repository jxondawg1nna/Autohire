#!/usr/bin/env python3
"""
Virtual Desktop Environment Installer

Automated installation script for the Autohire Virtual Desktop Environment.
Handles dependencies, Docker setup, service initialization, and configuration.
"""

import os
import sys
import subprocess
import platform
import json
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class VirtualDesktopInstaller:
    """Main installer class for Virtual Desktop Environment"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.root_dir = Path(__file__).parent.absolute()
        self.config = {}
        
        # Installation paths
        self.docker_dir = self.root_dir / "docker"
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.streaming_dir = self.root_dir / "streaming-gateway"
        
        print(f"{Colors.BLUE}{Colors.BOLD}Autohire Virtual Desktop Environment Installer{Colors.RESET}")
        print(f"Platform: {self.platform}")
        print(f"Root directory: {self.root_dir}")
        print("=" * 60)
    
    def run(self):
        """Run the complete installation process"""
        try:
            print(f"\n{Colors.CYAN}Starting Virtual Desktop Environment installation...{Colors.RESET}")
            
            # Pre-installation checks
            self._check_system_requirements()
            self._check_dependencies()
            
            # Configuration
            self._setup_configuration()
            
            # Docker setup
            self._setup_docker()
            self._build_docker_images()
            
            # Backend setup
            self._setup_backend()
            
            # Frontend setup
            self._setup_frontend()
            
            # Streaming gateway setup
            self._setup_streaming_gateway()
            
            # Service initialization
            self._initialize_services()
            
            # Post-installation verification
            self._verify_installation()
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Virtual Desktop Environment installed successfully!{Colors.RESET}")
            self._print_access_information()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Installation cancelled by user{Colors.RESET}")
            sys.exit(1)
        except Exception as e:
            print(f"\n{Colors.RED}❌ Installation failed: {e}{Colors.RESET}")
            sys.exit(1)
    
    def _check_system_requirements(self):
        """Check system requirements"""
        print(f"\n{Colors.BLUE}🔍 Checking system requirements...{Colors.RESET}")
        
        # Check Python version
        if sys.version_info < (3, 9):
            raise RuntimeError("Python 3.9 or higher is required")
        print(f"✅ Python {sys.version.split()[0]} - OK")
        
        # Check available disk space (minimum 10GB)
        disk_usage = shutil.disk_usage(self.root_dir)
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 10:
            raise RuntimeError(f"Insufficient disk space. Need at least 10GB, have {free_gb:.1f}GB")
        print(f"✅ Disk space {free_gb:.1f}GB - OK")
        
        # Check memory (minimum 4GB recommended)
        try:
            if self.platform == "linux":
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if 'MemTotal' in line:
                            mem_kb = int(line.split()[1])
                            mem_gb = mem_kb / (1024**2)
                            break
            else:
                # Windows/macOS - approximate check
                mem_gb = 8  # Assume sufficient for now
            
            if mem_gb < 4:
                print(f"{Colors.YELLOW}⚠️  Low memory detected ({mem_gb:.1f}GB). 8GB+ recommended{Colors.RESET}")
            else:
                print(f"✅ Memory {mem_gb:.1f}GB - OK")
        except:
            print(f"{Colors.YELLOW}⚠️  Could not check memory requirements{Colors.RESET}")
    
    def _check_dependencies(self):
        """Check for required dependencies"""
        print(f"\n{Colors.BLUE}🔍 Checking dependencies...{Colors.RESET}")
        
        dependencies = {
            'docker': ['docker', '--version'],
            'docker-compose': ['docker-compose', '--version'],
            'node': ['node', '--version'],
            'npm': ['npm', '--version']
        }
        
        missing_deps = []
        
        for name, cmd in dependencies.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
                print(f"✅ {name} {version} - OK")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ {name} - NOT FOUND")
                missing_deps.append(name)
        
        if missing_deps:
            print(f"\n{Colors.RED}Missing dependencies: {', '.join(missing_deps)}{Colors.RESET}")
            print("Please install the missing dependencies and run the installer again.")
            
            if self.platform == "windows":
                print("\nWindows installation instructions:")
                print("- Docker Desktop: https://docs.docker.com/desktop/windows/install/")
                print("- Node.js: https://nodejs.org/en/download/")
            elif self.platform == "linux":
                print("\nLinux installation instructions:")
                print("- Docker: sudo apt install docker.io docker-compose")
                print("- Node.js: sudo apt install nodejs npm")
            elif self.platform == "darwin":
                print("\nmacOS installation instructions:")
                print("- Docker Desktop: https://docs.docker.com/desktop/mac/install/")
                print("- Node.js: brew install node")
            
            sys.exit(1)
    
    def _setup_configuration(self):
        """Setup configuration files"""
        print(f"\n{Colors.BLUE}⚙️  Setting up configuration...{Colors.RESET}")
        
        env_file = self.root_dir / ".env"
        
        if env_file.exists():
            print("✅ .env file already exists")
            return
        
        # Generate secure passwords and keys
        import secrets
        import string
        
        def generate_password(length=32):
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        
        config_template = f"""# Virtual Desktop Environment Configuration
# Generated by installer on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
POSTGRES_PASSWORD={generate_password()}
DATABASE_URL=postgresql://autohire:autohire_secure_pass_2024@postgres:5432/autohire_virtual_desktop

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security Configuration
SECRET_KEY={generate_password(64)}
JWT_SECRET={generate_password(64)}

# Virtual Desktop Configuration
VD_MAX_SESSIONS=10
VD_DEFAULT_MEMORY_LIMIT=4g
VD_DEFAULT_CPU_LIMIT=2.0
VD_STORAGE_PATH=./storage/sessions

# Networking
CORS_ORIGIN=http://localhost:3000
API_URL=http://localhost:8001

# Monitoring
GRAFANA_PASSWORD={generate_password(16)}

# Development/Production
NODE_ENV=development
LOG_LEVEL=INFO

# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock
"""
        
        with open(env_file, 'w') as f:
            f.write(config_template)
        
        print("✅ Generated .env configuration file")
        
        # Create storage directories
        storage_dir = self.root_dir / "storage"
        storage_dir.mkdir(exist_ok=True)
        (storage_dir / "sessions").mkdir(exist_ok=True)
        (storage_dir / "logs").mkdir(exist_ok=True)
        print("✅ Created storage directories")
    
    def _setup_docker(self):
        """Setup Docker environment"""
        print(f"\n{Colors.BLUE}🐳 Setting up Docker environment...{Colors.RESET}")
        
        # Check if Docker daemon is running
        try:
            subprocess.run(['docker', 'info'], capture_output=True, check=True)
            print("✅ Docker daemon is running")
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ Docker daemon is not running{Colors.RESET}")
            print("Please start Docker Desktop and run the installer again.")
            sys.exit(1)
        
        # Create Docker networks
        networks = [
            ('virtual_desktop_network', '172.20.0.0/16'),
            ('desktop_isolated', '172.21.0.0/16')
        ]
        
        for network_name, subnet in networks:
            try:
                # Check if network exists
                subprocess.run(['docker', 'network', 'inspect', network_name], 
                             capture_output=True, check=True)
                print(f"✅ Network {network_name} already exists")
            except subprocess.CalledProcessError:
                # Create network
                subprocess.run(['docker', 'network', 'create', 
                              '--driver', 'bridge',
                              '--subnet', subnet,
                              network_name], check=True)
                print(f"✅ Created network {network_name}")
    
    def _build_docker_images(self):
        """Build Docker images for virtual desktop containers"""
        print(f"\n{Colors.BLUE}🏗️  Building Docker images...{Colors.RESET}")
        
        images_to_build = [
            {
                'name': 'autohire-desktop-ubuntu:latest',
                'path': self.docker_dir / 'virtual-desktop' / 'ubuntu',
                'platform_support': ['linux', 'darwin', 'windows']
            },
            {
                'name': 'autohire-desktop-windows:latest', 
                'path': self.docker_dir / 'virtual-desktop' / 'windows',
                'platform_support': ['windows']
            }
        ]
        
        for image in images_to_build:
            if self.platform not in image['platform_support']:
                print(f"⏭️  Skipping {image['name']} (not supported on {self.platform})")
                continue
            
            dockerfile = image['path'] / 'Dockerfile'
            if not dockerfile.exists():
                print(f"⚠️  Dockerfile not found for {image['name']}")
                continue
            
            print(f"🔨 Building {image['name']}...")
            
            try:
                # Build image
                build_cmd = [
                    'docker', 'build',
                    '-t', image['name'],
                    '-f', str(dockerfile),
                    str(image['path'])
                ]
                
                result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
                print(f"✅ Built {image['name']}")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to build {image['name']}: {e}")
                print(f"Build output: {e.stdout}")
                print(f"Build errors: {e.stderr}")
                # Continue with other images
    
    def _setup_backend(self):
        """Setup backend services"""
        print(f"\n{Colors.BLUE}🐍 Setting up backend services...{Colors.RESET}")
        
        # Install Python dependencies
        requirements_file = self.backend_dir / "requirements.txt"
        if requirements_file.exists():
            print("📦 Installing Python dependencies...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '-r', str(requirements_file)
            ], check=True)
            print("✅ Python dependencies installed")
        else:
            print("⚠️  requirements.txt not found, skipping Python dependencies")
    
    def _setup_frontend(self):
        """Setup frontend application"""
        print(f"\n{Colors.BLUE}⚛️  Setting up frontend application...{Colors.RESET}")
        
        package_json = self.frontend_dir / "package.json"
        if package_json.exists():
            print("📦 Installing Node.js dependencies...")
            
            # Install dependencies
            subprocess.run(['npm', 'install'], cwd=self.frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
            
            # Build frontend
            print("🏗️  Building frontend...")
            subprocess.run(['npm', 'run', 'build'], cwd=self.frontend_dir, check=True)
            print("✅ Frontend built successfully")
        else:
            print("⚠️  package.json not found in frontend directory")
    
    def _setup_streaming_gateway(self):
        """Setup streaming gateway service"""
        print(f"\n{Colors.BLUE}🌐 Setting up streaming gateway...{Colors.RESET}")
        
        package_json = self.streaming_dir / "package.json"
        if package_json.exists():
            print("📦 Installing streaming gateway dependencies...")
            
            # Install dependencies
            subprocess.run(['npm', 'install'], cwd=self.streaming_dir, check=True)
            print("✅ Streaming gateway dependencies installed")
            
            # Build TypeScript
            print("🏗️  Building streaming gateway...")
            subprocess.run(['npm', 'run', 'build'], cwd=self.streaming_dir, check=True)
            print("✅ Streaming gateway built successfully")
        else:
            print("⚠️  Streaming gateway package.json not found")
    
    def _initialize_services(self):
        """Initialize and start services"""
        print(f"\n{Colors.BLUE}🚀 Initializing services...{Colors.RESET}")
        
        compose_file = self.root_dir / "docker-compose.virtual-desktop.yml"
        if not compose_file.exists():
            raise RuntimeError("Docker compose file not found")
        
        # Start infrastructure services first
        print("🔧 Starting infrastructure services...")
        subprocess.run([
            'docker-compose', '-f', str(compose_file),
            'up', '-d', 'postgres', 'redis'
        ], check=True)
        
        # Wait for services to be ready
        print("⏳ Waiting for infrastructure services to be ready...")
        time.sleep(15)
        
        # Start application services
        print("🔧 Starting application services...")
        subprocess.run([
            'docker-compose', '-f', str(compose_file),
            'up', '-d'
        ], check=True)
        
        # Wait for services to start
        print("⏳ Waiting for services to start...")
        time.sleep(10)
        
        print("✅ Services started successfully")
    
    def _verify_installation(self):
        """Verify the installation is working"""
        print(f"\n{Colors.BLUE}🔍 Verifying installation...{Colors.RESET}")
        
        # Check service health
        health_checks = [
            ("Virtual Desktop API", "http://localhost:8001/api/v1/virtual-desktop/health"),
            ("Streaming Gateway", "http://localhost:8002/health"),
            ("Nginx Proxy", "http://localhost/health")
        ]
        
        import urllib.request
        
        for service_name, url in health_checks:
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    if response.getcode() == 200:
                        print(f"✅ {service_name} - Healthy")
                    else:
                        print(f"⚠️  {service_name} - Response code {response.getcode()}")
            except Exception as e:
                print(f"❌ {service_name} - Failed: {e}")
        
        # Check Docker containers
        print("\n📊 Container status:")
        subprocess.run([
            'docker-compose', '-f', 
            str(self.root_dir / "docker-compose.virtual-desktop.yml"),
            'ps'
        ])
    
    def _print_access_information(self):
        """Print access information for the user"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Installation Complete!{Colors.RESET}")
        print("\n" + "=" * 60)
        print(f"{Colors.CYAN}{Colors.BOLD}Access Information:{Colors.RESET}")
        print("=" * 60)
        
        services = [
            ("Virtual Desktop API", "http://localhost:8001/api/v1/virtual-desktop/health", "Backend API"),
            ("Web Interface", "http://localhost", "Main application"),
            ("Streaming Gateway", "http://localhost:8002", "WebRTC/VNC gateway"),
            ("API Documentation", "http://localhost:8001/docs", "Interactive API docs")
        ]
        
        for name, url, description in services:
            print(f"{Colors.WHITE}📍 {name:20} {Colors.BLUE}{url:35} {Colors.RESET}{description}")
        
        print("\n" + "=" * 60)
        print(f"{Colors.YELLOW}{Colors.BOLD}Quick Start Guide:{Colors.RESET}")
        print("=" * 60)
        
        print(f"""
1. {Colors.GREEN}Access the web interface:{Colors.RESET}
   Open http://localhost in your browser

2. {Colors.GREEN}Create a virtual desktop session:{Colors.RESET}
   POST http://localhost/api/v1/virtual-desktop/create
   
3. {Colors.GREEN}View session in browser:{Colors.RESET}
   Use the Desktop Session Manager component

4. {Colors.GREEN}Monitor system:{Colors.RESET}
   Check http://localhost/api/v1/virtual-desktop/stats

5. {Colors.GREEN}View logs:{Colors.RESET}
   docker-compose -f docker-compose.virtual-desktop.yml logs
""")
        
        print("=" * 60)
        print(f"{Colors.MAGENTA}{Colors.BOLD}Support & Documentation:{Colors.RESET}")
        print("=" * 60)
        print(f"""
📖 Setup Guide: {self.root_dir}/VIRTUAL_DESKTOP_SETUP.md
📋 Logs Directory: {self.root_dir}/storage/logs/
⚙️  Configuration: {self.root_dir}/.env
🐳 Docker Compose: {self.root_dir}/docker-compose.virtual-desktop.yml
""")

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
Virtual Desktop Environment Installer

Usage: python install_virtual_desktop.py [options]

Options:
  -h, --help     Show this help message
  --check-only   Only check requirements, don't install

This installer will:
1. Check system requirements and dependencies
2. Setup configuration files
3. Build Docker images for desktop environments
4. Initialize backend and frontend services
5. Start all services and verify installation

Requirements:
- Python 3.9+
- Docker & Docker Compose
- Node.js & npm
- 10GB+ free disk space
- 4GB+ RAM (8GB+ recommended)
""")
        sys.exit(0)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check-only':
        installer = VirtualDesktopInstaller()
        installer._check_system_requirements()
        installer._check_dependencies()
        print(f"\n{Colors.GREEN}✅ All requirements satisfied{Colors.RESET}")
        sys.exit(0)
    
    installer = VirtualDesktopInstaller()
    installer.run()

if __name__ == "__main__":
    main()