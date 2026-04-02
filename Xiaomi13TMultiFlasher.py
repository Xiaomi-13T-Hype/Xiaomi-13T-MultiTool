import os
import subprocess
import webbrowser
import time
import threading
from enum import Enum
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import io
import base64

class MenuAction(Enum):
    RUN_BAT = 1
    SHOW_LINK = 2
    OPEN_URL = 3
    RUN_EXE = 4
    NOT_WORKING = 5

class MenuItem:
    def __init__(self, name, action=None, action_data=None, submenu=None, path_segment=None):
        self.name = name
        self.action = action
        self.action_data = action_data
        self.submenu = submenu
        self.path_segment = path_segment or name


class FlashToolGUI:
    def __init__(self):
        # Get directory where script is located (portable)
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller creates temp folder
                self.base_path = os.path.join(os.path.dirname(sys.executable), '_internal')
            else:
                self.base_path = os.path.dirname(sys.executable)
            print(f"Running as EXE from: {self.base_path}")
        else:
            # Running as script
            self.base_path = os.path.dirname(os.path.abspath(__file__))
            print(f"Running as script from: {self.base_path}")
        
        print(f"Base path set to: {self.base_path}")
        self.current_path = self.base_path
        self.menu_stack = []
        self.custom_font = None  # Will store custom font
        self.bg_image = None  # Cache background image
        self.cached_fonts = {}  # Cache font objects
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Xiaomi 13T MultiTool")
        self.root.geometry("500x900")
        self.root.minsize(400, 700)
        
        # Setup styles and menu
        self.setup_styles()
        self.setup_menu()
        self.create_gui()
        
        # Bind keyboard shortcuts
        self.root.bind('<F1>', lambda: self.run_fastboot_flash_tool())
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def run_fastboot_flash_tool(self):
        """Run Fastboot Flashing Tool (XiaoMiFlash.exe)"""
        xiaomi_flash_path = os.path.join(self.base_path, "Fastboot flashing tool", "XiaoMiFlash.exe")
        if os.path.exists(xiaomi_flash_path):
            subprocess.Popen(f'"{xiaomi_flash_path}"', shell=True)
            self.update_status("Started Fastboot Flashing Tool (F1)")
        
    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        
        # Use a more compatible theme
        try:
            style.theme_use('clam')
        except:
            try:
                style.theme_use('alt')
            except:
                style.theme_use('default')
        
        # Configure custom font
        font_path = os.path.join(self.base_path, "Anime Ace v3.ttf")
        print(f"Looking for font at: {font_path}")
        
        if os.path.exists(font_path):
            try:
                # Register font for system
                import ctypes
                ctypes.windll.gdi32.AddFontResourceW(font_path, 0)
                print(f"Font registered from: {font_path}")
                
                # Create custom font object
                self.custom_font = ('Anime Ace v3', 12, 'bold')
                self.cached_fonts['custom'] = self.custom_font
                print("Custom font loaded successfully")
            except Exception as e:
                print(f"Error loading font: {e}")
                self.custom_font = None
        else:
            print(f"Font file not found at: {font_path}")
            self.custom_font = None
        
        # Load custom font with fallback
        try:
            # Try to load Anime Ace v3 font
            if self.custom_font is not None:
                # Cache font objects for reuse
                try:
                    self.cached_fonts['bold'] = ('Anime Ace v3', 16, 'bold')
                    self.cached_fonts['small'] = ('Anime Ace v3', 10)
                    self.cached_fonts['button'] = ('Anime Ace v3', 10)
                    # Store custom font for use in buttons
                    self.custom_font = "Anime Ace v3"
                    
                    # Configure styles with cached font
                    style.configure('Title.TLabel', 
                                   font=self.cached_fonts['bold'],
                                   foreground='white',
                                   background='#1a1a2e')
                    
                    style.configure('Subtitle.TLabel', 
                                   font=self.cached_fonts['small'],
                                   foreground='#e0e0e0',
                                   background='#1a1a2e')
                    
                    style.configure('Menu.TButton',
                                   font=self.cached_fonts['button'],
                                   padding=(10, 5),
                                   background='#4facfe',
                                   foreground='white')
                    
                except Exception as font_error:
                    print(f"Error creating font objects: {font_error}")
                    raise Exception("Font creation failed")
            else:
                raise FileNotFoundError("Font file not found")
        except Exception as e:
            print(f"Could not load custom font, using system fonts: {e}")
            self.custom_font = None  # Reset to None
            # Fallback to system fonts
            try:
                style.configure('Title.TLabel', 
                               font=('Arial', 16, 'bold'), 
                               foreground='white',
                               background='#1a1a2e')
            except:
                pass
            
            try:
                style.configure('Subtitle.TLabel', 
                               font=('Arial', 10), 
                               foreground='#e0e0e0',
                               background='#1a1a2e')
            except:
                pass
            
            try:
                style.configure('Menu.TButton',
                               font=('Arial', 10),
                               padding=(10, 5),
                               background='#4facfe',
                               foreground='white')
            except:
                pass
        
        try:
            style.map('Menu.TButton',
                     background=[('active', '#00f2fe')])
        except:
            pass
    
    def load_background_image(self):
        """Load and cache the background image"""
        if self.bg_image is not None:
            return self.bg_image  # Return cached image
            
        try:
            # Load the attached background image
            bg_path = os.path.join("attached_assets", "30389_1754247107832.jpg")
            if os.path.exists(bg_path):
                img = Image.open(bg_path)
                
                # Crop the borders - remove 50 pixels from each side
                width, height = img.size
                crop_amount = 50
                
                # Ensure we don't crop too much
                if width > crop_amount * 2 and height > crop_amount * 2:
                    img = img.crop((
                        crop_amount,  # left
                        crop_amount,  # top
                        width - crop_amount,  # right
                        height - crop_amount  # bottom
                    ))
                
                # Resize to match window size
                img = img.resize((500, 900), Image.Resampling.LANCZOS)
                
                self.bg_image = ImageTk.PhotoImage(img)
                return self.bg_image
            else:
                # Fallback to generated gradient
                return self.create_background()
        except Exception as e:
            print(f"Error loading background image: {e}")
            return self.create_background()
    
    def create_background(self):
        """Create gradient background as fallback"""
        width, height = 500, 900
        
        # Create gradient from blue to pink
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        if pixels is not None:
            for y in range(height):
                for x in range(width):
                    # Calculate gradient position (0.0 to 1.0)
                    pos_x = x / width
                    pos_y = y / height
                    
                    # Blue to cyan to pink gradient
                    r = int(79 + (255 - 79) * (pos_x * 0.5 + pos_y * 0.5))
                    g = int(172 + (105 - 172) * pos_y)
                    b = int(254 - (254 - 180) * pos_x)
                    
                    pixels[x, y] = (r, g, b)
        
        return ImageTk.PhotoImage(img)
    
    def create_gui(self):
        """Create the main GUI"""
        # Create background
        self.bg_image = self.load_background_image()
        
        # Main container with background
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Background label
        self.bg_label = tk.Label(self.main_frame, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Content frame with semi-transparent background
        self.content_frame = tk.Frame(self.main_frame, bg='#1a1a2e', relief='raised', bd=2)
        self.content_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Title section
        self.title_frame = tk.Frame(self.content_frame, bg='#1a1a2e')
        self.title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.title_label = ttk.Label(self.title_frame, 
                                   text="Xiaomi 13T MultiTool",
                                   style='Title.TLabel')
        self.title_label.pack()
        
        self.subtitle_label = ttk.Label(self.title_frame,
                                      text="",
                                      style='Subtitle.TLabel')
        self.subtitle_label.pack()
        
        # Main content area
        self.main_content = tk.Frame(self.content_frame, bg='#1a1a2e')
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Menu navigation (full width)
        self.menu_frame = tk.Frame(self.main_content, bg='#2e2e3e', relief='raised', bd=1)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))
        
        # Navigation header
        self.nav_header = ttk.Label(self.menu_frame, text="Navigation", style='Title.TLabel')
        self.nav_header.pack(pady=10)
        
        # Menu buttons frame (no scrollbar)
        self.menu_buttons_frame = tk.Frame(self.menu_frame, bg='#2e2e3e')
        self.menu_buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_menu_buttons()
        
        # Status bar
        self.status_frame = tk.Frame(self.content_frame, bg='#1a1a2e')
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        
        self.status_label = ttk.Label(self.status_frame, 
                                    text="Ready | Select an option from the menu",
                                    style='Subtitle.TLabel')
        self.status_label.pack()
    
    
    def create_menu_buttons(self):
        """Create menu navigation buttons"""
        # Clear existing buttons
        for widget in self.menu_buttons_frame.winfo_children():
            widget.destroy()
        
        # Get current menu
        current_menu = self.get_current_menu()
        
        # Use cached font
        button_font = self.cached_fonts.get('button', ('Arial', 10))
        
        # Back button if not at root
        if self.menu_stack:
            back_btn = tk.Button(self.menu_buttons_frame,
                               text="← Back",
                               command=self.go_back,
                               font=button_font,
                               bg='#4facfe',
                               fg='white',
                               relief='raised',
                               bd=2,
                               padx=10,
                               pady=5)
            back_btn.pack(fill=tk.X, pady=2, padx=5)
        
        # Show current path (only if not at root)
        if self.menu_stack:
            path_text = " > ".join([item.name for item in self.menu_stack])
            path_label = ttk.Label(self.menu_buttons_frame,
                                 text=path_text,
                                 style='Subtitle.TLabel',
                                 wraplength=200)
            path_label.pack(pady=5)
        
        # Menu items
        for idx, item in enumerate(current_menu):
            # Create a closure to capture the correct item
            def make_command(menu_item):
                return lambda: self.handle_menu_item(menu_item)
            
            btn = tk.Button(self.menu_buttons_frame,
                           text=item.name,
                           command=make_command(item),
                           font=button_font,
                           bg='#4facfe',
                           fg='white',
                           relief='raised',
                           bd=2,
                           padx=10,
                           pady=5)
            btn.pack(fill=tk.X, pady=2, padx=5)
    
    def setup_menu(self):
        """Setup the menu structure"""
        self.main_menu = [
            MenuItem("ADB/Fastboot Terminal", MenuAction.RUN_BAT, os.path.join("ADB_Fastboot_Terminal", "open_a_terminal_here.bat")),
            MenuItem("Fastboot Flash Tool", MenuAction.RUN_EXE, os.path.join("Fastboot_flash_tools", "XiaoMiFlash.exe")),
            MenuItem("Recovery", submenu=self.create_recovery_menu()),
            MenuItem("Root", submenu=self.create_root_menu()),
            MenuItem("Scrcpy", submenu=self.create_scrcpy_menu()),
            MenuItem("Unlocking bootloader", MenuAction.RUN_EXE, os.path.join("Unlocking_bootloader", "mi.exe"))
        ]
    
    def create_root_menu(self):
        """Create Root submenu with HyperOS 2 regional variants"""
        menu_items = []
        
        # Define all possible regions
        regions = [
            ("HyperOS 2 Europe", "HyperOS_2_EU"),
            ("HyperOS 2 Global", "HyperOS_2_GL"),
            ("HyperOS 2 India", "HyperOS_2_IN"),
            ("HyperOS 2 Russia", "HyperOS_2_RU"),
            ("HyperOS 2 Taiwan", "HyperOS_2_TA"),
            ("HyperOS 2 Turkey", "HyperOS_2_TY")
        ]
        
        # Check which folders exist
        stock_path = os.path.join(self.base_path, "Stock_KSU_SukiSU_Magisk")
        if os.path.exists(stock_path):
            available_folders = os.listdir(stock_path)
            
            for display_name, folder_name in regions:
                if folder_name in available_folders:
                    menu_items.append(MenuItem(display_name, submenu=self.create_hyperos_folder_menu(folder_name)))
        
        return menu_items
    
    def create_hyperos_folder_menu(self, folder_name):
        """Create menu items based on folders in the specified directory"""
        stock_path = os.path.join(self.base_path, "Stock_KSU_SukiSU_Magisk")
        print(f"Looking for folders in: {stock_path}")
        print(f"Available folders: {os.listdir(stock_path) if os.path.exists(stock_path) else 'Folder not found'}")
        
        # Try different folder name variants
        folder_variants = [
            folder_name,  # Original: "HyperOS_2_GL"
            folder_name.replace("_", " "),  # With spaces: "HyperOS 2 GL"
            folder_name.replace("_2_", " 2 "),  # With double space: "HyperOS 2 GL"
        ]
        
        menu_items = []
        found_folder = None
        
        for variant in folder_variants:
            folder_path = os.path.join(stock_path, variant)
            print(f"Looking for HyperOS folders in: {folder_path}")
            
            if os.path.exists(folder_path):
                try:
                    items = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
                    print(f"Found items: {items}")
                    
                    if not items:
                        print(f"No version folders found in {folder_path}")
                        return None  # Return None instead of empty list
                    else:
                        found_folder = variant
                        break
                except Exception as e:
                    print(f"Error reading folder {folder_path}: {e}")
        
        if found_folder:
            folder_path = os.path.join(stock_path, found_folder)
            print(f"Using found folder: {found_folder} at {folder_path}")
            
            try:
                items = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
                print(f"Found items: {items}")
                
                if not items:
                    print(f"No version folders found in {folder_path}")
                    return None  # Return None instead of empty list
                
                # Custom sort: first by digit count (fewer digits first), then by version order
                def custom_sort_key(item):
                    # Extract version numbers for proper sorting
                    parts = item.split('.')
                    # Count total digits in the version
                    digit_count = sum(len(part) for part in parts if part.isdigit())
                    # Create numeric tuple for version comparison
                    version_tuple = tuple(int(part) if part.isdigit() else 0 for part in parts)
                    return (digit_count, version_tuple)
                
                items.sort(key=custom_sort_key)
                
                for item in items:
                    # Create submenu for each version folder
                    version_path = os.path.join(folder_path, item)
                    submenu_items = self.create_version_menu_items(version_path)
                    # Replace underscores with spaces for display
                    display_name = item.replace('_', ' ')
                    menu_items.append(MenuItem(display_name, submenu=submenu_items, action=None, action_data=None))
            except Exception as e:
                print(f"Error reading folder {folder_path}: {e}")
        else:
            print(f"Folder not found: {folder_path}")
            return None
        
        return menu_items
    
    def create_version_menu_items(self, version_path):
        """Create menu items for files in a version folder with direct execution buttons"""
        menu_items = []
        
        if os.path.exists(version_path):
            try:
                files = [f for f in os.listdir(version_path) if os.path.isfile(os.path.join(version_path, f))]
                files.sort()
                
                # Extract version number from folder name for pattern matching
                folder_name = os.path.basename(version_path)
                version_pattern = folder_name.replace('HyperOS ', '').replace(' ', '')
                
                # Find files for each category
                stock_file = None
                ksu_file = None
                suki_file = None
                magisk_file = None
                
                # Find files for each category
                for file in files:
                    file_lower = file.lower()
                    
                    # Check for exact pattern matches first
                    if file_lower == f"{version_pattern}_stock.bat" or file_lower == f"{version_pattern}_stock.exe":
                        stock_file = file
                    elif file_lower == f"{version_pattern}_ksu.bat" or file_lower == f"{version_pattern}_ksu.exe":
                        ksu_file = file
                    elif file_lower == f"{version_pattern}_suki.bat" or file_lower == f"{version_pattern}_suki.exe":
                        suki_file = file
                    elif file_lower == f"{version_pattern}_magisk.bat" or file_lower == f"{version_pattern}_magisk.exe":
                        magisk_file = file
                    # Fallback to partial matches
                    elif 'stock' in file_lower and not stock_file:
                        stock_file = file
                    elif 'ksu' in file_lower and not ksu_file:
                        ksu_file = file
                    elif 'suki' in file_lower and not suki_file:
                        suki_file = file
                    elif 'magisk' in file_lower and not magisk_file:
                        magisk_file = file
                
                # Create buttons for all categories (always visible)
                # Stock button
                if stock_file:
                    relative_path = os.path.relpath(os.path.join(version_path, stock_file), self.base_path)
                    if stock_file.endswith('.bat'):
                        menu_items.append(MenuItem("Stock", MenuAction.RUN_BAT, relative_path))
                    elif stock_file.endswith('.exe'):
                        menu_items.append(MenuItem("Stock", MenuAction.RUN_EXE, relative_path))
                    else:
                        menu_items.append(MenuItem("Stock", MenuAction.SHOW_LINK, relative_path))
                else:
                    # Show button even if no file found
                    menu_items.append(MenuItem("Stock", MenuAction.NOT_WORKING, "No Stock file found"))
                
                # KSU button
                if ksu_file:
                    relative_path = os.path.relpath(os.path.join(version_path, ksu_file), self.base_path)
                    if ksu_file.endswith('.bat'):
                        menu_items.append(MenuItem("KSU", MenuAction.RUN_BAT, relative_path))
                    elif ksu_file.endswith('.exe'):
                        menu_items.append(MenuItem("KSU", MenuAction.RUN_EXE, relative_path))
                    else:
                        menu_items.append(MenuItem("KSU", MenuAction.SHOW_LINK, relative_path))
                else:
                    # Show button even if no file found
                    menu_items.append(MenuItem("KSU", MenuAction.NOT_WORKING, "No KSU file found"))
                
                # SukiSU button
                if suki_file:
                    relative_path = os.path.relpath(os.path.join(version_path, suki_file), self.base_path)
                    if suki_file.endswith('.bat'):
                        menu_items.append(MenuItem("SukiSU", MenuAction.RUN_BAT, relative_path))
                    elif suki_file.endswith('.exe'):
                        menu_items.append(MenuItem("SukiSU", MenuAction.RUN_EXE, relative_path))
                    else:
                        menu_items.append(MenuItem("SukiSU", MenuAction.SHOW_LINK, relative_path))
                else:
                    # Show button even if no file found
                    menu_items.append(MenuItem("SukiSU", MenuAction.NOT_WORKING, "No SukiSU file found"))
                
                # Magisk button
                if magisk_file:
                    relative_path = os.path.relpath(os.path.join(version_path, magisk_file), self.base_path)
                    if magisk_file.endswith('.bat'):
                        menu_items.append(MenuItem("Magisk", MenuAction.RUN_BAT, relative_path))
                    elif magisk_file.endswith('.exe'):
                        menu_items.append(MenuItem("Magisk", MenuAction.RUN_EXE, relative_path))
                    else:
                        menu_items.append(MenuItem("Magisk", MenuAction.SHOW_LINK, relative_path))
                else:
                    # Show button even if no file found
                    menu_items.append(MenuItem("Magisk", MenuAction.NOT_WORKING, "No Magisk file found"))
                            
            except Exception as e:
                print(f"Error reading version folder {version_path}: {e}")
        
        return menu_items
    
    def create_recovery_menu(self):
        """Create Recovery submenu"""
        recovery_path = os.path.join(self.base_path, "Recovery")
        menu_items = []
        
        # Add specific recovery options
        menu_items.extend([
            MenuItem("PBRP", MenuAction.RUN_BAT, os.path.join("Recovery", "PBRP", "PBRP_Flash.bat")),
            MenuItem("TWRP", MenuAction.RUN_BAT, os.path.join("Recovery", "TWRP", "TWRP_Flash.bat")),
            MenuItem("OrangeFox", MenuAction.RUN_BAT, os.path.join("Recovery", "OrangeFox", "OrangeFox_Flash.bat"))
        ])
        
        # Also show existing files in Recovery folder
        if os.path.exists(recovery_path):
            try:
                files = [f for f in os.listdir(recovery_path) if os.path.isfile(os.path.join(recovery_path, f))]
                files.sort()
                
                for file in files:
                    if file.endswith('.bat') and file not in ["PBRP_Flash.bat", "TWRP_Flash.bat", "OrangeFox_Flash.bat"]:
                        relative_path = os.path.relpath(os.path.join(recovery_path, file), self.base_path)
                        menu_items.append(MenuItem(file, MenuAction.RUN_BAT, relative_path))
                    elif file.endswith('.exe'):
                        relative_path = os.path.relpath(os.path.join(recovery_path, file), self.base_path)
                        menu_items.append(MenuItem(file, MenuAction.RUN_EXE, relative_path))
                    else:
                        relative_path = os.path.relpath(os.path.join(recovery_path, file), self.base_path)
                        menu_items.append(MenuItem(file, MenuAction.SHOW_LINK, relative_path))
            except Exception as e:
                print(f"Error reading Recovery folder: {e}")
        
        return menu_items
    
    def create_official_firmwares_menu(self):
        """Create Official firmwares submenu"""
        firmware_path = os.path.join(self.base_path, "Official firmware")
        menu_items = []
        
        if os.path.exists(firmware_path):
            try:
                files = [f for f in os.listdir(firmware_path) if os.path.isfile(os.path.join(firmware_path, f))]
                files.sort()
                
                for file in files:
                    if file.endswith('.bat'):
                        relative_path = os.path.relpath(os.path.join(firmware_path, file), self.base_path)
                        menu_items.append(MenuItem(file, MenuAction.RUN_BAT, relative_path))
                    elif file.endswith('.exe'):
                        relative_path = os.path.relpath(os.path.join(firmware_path, file), self.base_path)
                        menu_items.append(MenuItem(file, MenuAction.RUN_EXE, relative_path))
                    else:
                        relative_path = os.path.relpath(os.path.join(firmware_path, file), self.base_path)
                        menu_items.append(MenuItem(file, MenuAction.SHOW_LINK, relative_path))
            except Exception as e:
                print(f"Error reading Official firmware folder: {e}")
        
        return menu_items
    
    def create_fastboot_flashing_tool_menu(self):
        """Create Fastboot Flashing Tool submenu"""
        fastboot_path = os.path.join(self.base_path, "Fastboot Flashing Tool")
        menu_items = []
        
        # Only add XiaoMiFlash - hide all other files
        xiaomi_flash_path = os.path.join(fastboot_path, "XiaoMiFlash.exe")
        if os.path.exists(xiaomi_flash_path):
            relative_path = os.path.relpath(xiaomi_flash_path, self.base_path)
            menu_items.append(MenuItem("Fastboot Flashing Tool", MenuAction.RUN_EXE, relative_path))
        
        return menu_items
    
    def create_unlocking_menu(self):
        """Create Unlocking bootloader submenu"""
        unlock_path = os.path.join(self.base_path, "Unlocking bootloader")
        menu_items = []
        
        # Add specific unlocking tools
        miunlock_path = os.path.join(unlock_path, "miflash_unlock.exe")
        if os.path.exists(miunlock_path):
            relative_path = os.path.relpath(miunlock_path, self.base_path)
            menu_items.append(MenuItem("MiUnlockTool", MenuAction.RUN_EXE, relative_path))
        
        auto_unlock_path = os.path.join(unlock_path, "mi.exe")
        if os.path.exists(auto_unlock_path):
            relative_path = os.path.relpath(auto_unlock_path, self.base_path)
            menu_items.append(MenuItem("Automatic application for Unlocking Bootloader (HyperOS 1+)", MenuAction.RUN_EXE, relative_path))
        
        return menu_items
    
    def get_current_menu(self):
        """Get current menu based on navigation stack"""
        current = self.main_menu
        for item in self.menu_stack:
            if item.submenu:
                current = item.submenu
            else:
                break
        return current
    
    def handle_menu_item(self, item):
        """Handle menu item selection"""
        print(f"=== handle_menu_item called for: {item.name} ===")
        print(f"submenu: {item.submenu}")
        print(f"submenu type: {type(item.submenu)}")
        print(f"submenu bool: {bool(item.submenu)}")
        print(f"submenu is None: {item.submenu is None}")
        
        if item.submenu and item.submenu is not None:
            # Navigate to submenu
            print("Taking submenu branch")
            self.menu_stack.append(item)
            self.create_menu_buttons()
            self.update_status(f"Navigated to: {item.name}")
        else:
            # Execute action
            print("Taking execute_action branch")
            self.execute_action(item)
    
    def execute_action(self, item):
        """Execute menu action"""
        try:
            print(f"Executing action for: {item.name}, submenu: {item.submenu is not None}, action: {item.action}")
            
            # Skip if item has submenu (should be handled in handle_menu_item)
            if item.submenu:
                self.update_status(f"Navigation item: {item.name}")
                return
            
            # Skip if action is None (navigation item)
            if item.action is None:
                self.update_status(f"Navigation item: {item.name}")
                return
                
            if item.action == MenuAction.RUN_BAT:
                self.run_bat_file(item.action_data)
            
            elif item.action == MenuAction.RUN_EXE:
                self.run_exe_file(item.action_data)
            
            elif item.action == MenuAction.SHOW_LINK:
                self.update_status(f"Showing info: {item.name}")
                messagebox.showinfo("Information", item.action_data)
            
            elif item.action == MenuAction.OPEN_URL:
                webbrowser.open(item.action_data)
                self.update_status(f"Opened URL: {item.action_data}")
            
            elif item.action == MenuAction.NOT_WORKING:
                self.update_status(f"Feature not working: {item.action_data}")
                messagebox.showwarning("Not Working", item.action_data)
            
            else:
                self.update_status(f"Unknown action: {item.action} for item: {item.name}")
                messagebox.showwarning("Unknown Action", f"Unknown action for: {item.name}")
                
        except Exception as e:
            error_msg = f"Error executing action for {item.name}: {str(e)}"
            print(error_msg)
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def run_bat_file(self, relative_path):
        """Run .bat file"""
        full_path = os.path.join(self.base_path, relative_path)
        
        print(f"Attempting to run .bat file: {full_path}")
        print(f"File exists: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
        
        self.update_status(f"Running: {full_path}")
        
        # Use start command to open in new console window with auto-close
        command = f'start "Batch File" /D "{os.path.dirname(full_path)}" cmd /c "{full_path}"'
        print(f"Executing command: {command}")
        
        try:
            process = subprocess.Popen(command, shell=True)
            print(f"Process started with PID: {process.pid}")
        except Exception as e:
            print(f"Error starting process: {e}")
            raise
    
    def run_exe_file(self, relative_path):
        """Run .exe file"""
        full_path = os.path.join(self.base_path, relative_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
        
        # Debug: open console window to see what's happening
        if getattr(sys, 'frozen', False):
            # Running as exe - show console for debugging
            self.update_status(f"Running: {full_path} (console mode)")
            subprocess.Popen(f'"{full_path}"', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            self.update_status(f"Running: {full_path}")
            subprocess.Popen(f'"{full_path}"', shell=True)
    
    def go_back(self):
        """Go back in menu navigation"""
        if self.menu_stack:
            self.menu_stack.pop()
            self.create_menu_buttons()
            self.update_status("Navigated back")
    
    def update_status(self, message):
        """Update status bar"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"{timestamp} | {message}")
    
    def create_scrcpy_menu(self):
        """Create Scrcpy submenu with Win32 and Win64 options"""
        return [
            MenuItem("Win32", MenuAction.RUN_EXE, os.path.join("Scrcpy", "Scrcpy_WIN32", "scrcpy.exe")),
            MenuItem("Win64", MenuAction.RUN_EXE, os.path.join("Scrcpy", "Scrcpy_WIN64", "scrcpy.exe"))
        ]
    
    def on_closing(self):
        """Handle window closing event"""
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        try:
            self.update_status("Application started successfully")
            self.root.mainloop()
        except Exception as e:
            print(f"Error running application: {e}")
            messagebox.showerror("Error", f"Application error: {e}")

if __name__ == "__main__":
    try:
        app = FlashToolGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        # Show a basic error window even if main GUI fails
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")