#!/usr/bin/env python3
"""
Dependency installer for Xiaomi 13T MultiFlasher v1.3
Installs all required packages for the application (without music player)
"""

import subprocess
import sys
import platform
import os
import threading
import time

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def auto_press_y(process):
    """Automatically press 'y' every 10 seconds for a process"""
    try:
        while process.poll() is None:  # While process is still running
            time.sleep(10)
            if process.poll() is None:  # Check again before sending
                process.stdin.write('y\n')
                process.stdin.flush()
                print("🔸 Automatically pressed 'y'")
    except:
        pass

def install_adb_installer():
    """Install Fastboot/ADB Drivers"""
    system = platform.system()
    if system != "Windows":
        print("⚠ Fastboot/ADB Drivers are only available for Windows")
        return True
    
    adb_path = os.path.join(os.getcwd(), "Fastboot mode", "15 Second ADB Installer v1.5.6.exe")
    
    if not os.path.exists(adb_path):
        print(f"❌ Fastboot/ADB Drivers not found at: {adb_path}")
        return False
    
    print("🔧 Installing Fastboot/ADB Drivers...")
    try:
        # Start the process with stdin pipe
        process = subprocess.Popen(
            [adb_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Start auto-press thread
        press_thread = threading.Thread(target=auto_press_y, args=(process,))
        press_thread.daemon = True
        press_thread.start()
        
        # Wait for process to complete
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("✅ Fastboot/ADB Drivers installed successfully")
            return True
        else:
            print(f"❌ Fastboot/ADB Drivers failed with return code: {process.returncode}")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to install Fastboot/ADB Drivers: {e}")
        return False

def install_system_dependencies():
    """Install system-level dependencies for specific platforms"""
    system = platform.system()
    print(f"🖥️  Detected system: {system}")
    
    if system == "Linux":
        print("🔧 Installing Linux system dependencies...")
        try:
            # Ubuntu/Debian
            if os.path.exists("/etc/debian_version"):
                subprocess.check_call(
                    ["sudo", "apt-get", "install", "-y", 
                     "python3-tk", "python3-dev"]
                )
            # Fedora/CentOS
            elif os.path.exists("/etc/redhat-release"):
                subprocess.check_call(
                    ["sudo", "dnf", "install", "-y", 
                     "python3-tkinter", "python3-devel"]
                )
            print("✅ Linux dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Linux dependencies")
            return False
    
    elif system == "Darwin":  # macOS
        print("🍎 macOS detected - no additional system dependencies required")
        return True
    
    elif system == "Windows":
        print("🪟 Windows detected - no additional system dependencies required")
        return True
    
    return False

def main():
    """Install all required dependencies"""
    print("="*50)
    print("🚀 Installing Xiaomi 13T MultiFlasher dependencies")
    print("="*50)
    
    # First install system-level dependencies
    sys_success = install_system_dependencies()
    
    # Install Fastboot/ADB Drivers (Windows only)
    adb_success = True
    if platform.system() == "Windows":
        adb_success = install_adb_installer()
    
    # Python packages to install
    packages = [
        "pillow>=10.0.0",           # For image processing
        "pyinstaller",              # For creating executables
        "pywin32; platform_system=='Windows'",  # Windows API integration
        "requests",                 # For potential future web features
        "setuptools",               # For package management
        "wheel"                     # For building packages
    ]
    
    print("\n📦 Installing Python packages...")
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "="*50)
    print(f"📊 Installation summary:")
    print(f"- System dependencies: {'✅' if sys_success else '❌'}")
    if platform.system() == "Windows":
        print(f"- Fastboot/ADB Drivers: {'✅' if adb_success else '❌'}")
    print(f"- Python packages: {success_count}/{len(packages)} installed")
    
    if sys_success and adb_success and success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("You can now run: python Xiaomi13TMultiFlasher.py")
    else:
        print("\n⚠ Some components failed to install:")
        if not sys_success:
            print("- System dependencies installation failed")
        if platform.system() == "Windows" and not adb_success:
            print("- Fastboot/ADB Drivers installation failed")
        if success_count < len(packages):
            print(f"- {len(packages) - success_count} Python packages failed to install")
        
        print("\nTroubleshooting tips:")
        print("1. Make sure you have Python 3.8+ installed")
        print("2. Try running as administrator/root")
        print("3. Update pip: python -m pip install --upgrade pip")
        
        # Platform-specific troubleshooting
        system = platform.system()
        if system == "Windows":
            print("4. Install Microsoft Build Tools: https://aka.ms/buildtools")
        elif system == "Linux":
            print("4. Try: sudo apt update && sudo apt upgrade")
        elif system == "Darwin":
            print("4. Make sure Xcode Command Line Tools are installed: xcode-select --install")
    
    print("="*50)

if __name__ == "__main__":
    main()