#!/usr/bin/env python3
"""
╦ ╦╔═╗╔╗ ╔╗ ╔═╗╦═╗
║║║║╣ ╠╩╗╠╩╗║╣ ╠╦╝
╚╩╝╚═╝╚═╝╚═╝╚═╝╩╚═
Advanced Web Traffic Simulator
For HTB/CTF and Authorized Testing Only
"""

import sys
import time
import os
import json
import random
import threading
import argparse
import subprocess
from datetime import datetime
from collections import deque
from urllib.parse import quote_plus, urljoin, urlparse
import uuid
import platform

# Required libraries with import check
REQUIRED_PACKAGES = {
    'requests': 'requests',
    'bs4': 'beautifulsoup4',
    'psutil': 'psutil'
}

def check_and_install_dependencies():
    """Check for required packages and offer to install missing ones"""
    missing_packages = []
    
    # Check each required package
    for import_name, package_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if not missing_packages:
        return True
    
    # Display missing packages
    print(f"\n{Colors.RED}╔═══════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.RED}║   MISSING REQUIRED DEPENDENCIES      ║{Colors.ENDC}")
    print(f"{Colors.RED}╚═══════════════════════════════════════╝{Colors.ENDC}\n")
    
    print(f"{Colors.YELLOW}The following packages are required:{Colors.ENDC}")
    for pkg in missing_packages:
        print(f"  • {pkg}")
    
    print(f"\n{Colors.CYAN}Would you like to install them automatically?{Colors.ENDC}")
    choice = input(f"{Colors.GREEN}[Y/n]: {Colors.ENDC}").strip().lower()
    
    if choice in ['', 'y', 'yes']:
        return install_packages(missing_packages)
    else:
        print(f"\n{Colors.YELLOW}Manual installation command:{Colors.ENDC}")
        print(f"  pip install {' '.join(missing_packages)}")
        print(f"\n{Colors.RED}Exiting...{Colors.ENDC}\n")
        return False

def install_packages(packages):
    """Install packages using pip"""
    print(f"\n{Colors.CYAN}Installing packages...{Colors.ENDC}\n")
    
    # Determine pip command
    pip_commands = ['pip3', 'pip', 'python3 -m pip', 'python -m pip']
    pip_cmd = None
    
    for cmd in pip_commands:
        try:
            result = subprocess.run(
                cmd.split() + ['--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                pip_cmd = cmd.split()
                break
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    if not pip_cmd:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} Could not find pip!")
        print(f"{Colors.YELLOW}Please install pip first or manually install:{Colors.ENDC}")
        print(f"  pip install {' '.join(packages)}")
        return False
    
    # Install each package
    for package in packages:
        print(f"{Colors.CYAN}Installing {package}...{Colors.ENDC}")
        try:
            result = subprocess.run(
                pip_cmd + ['install', package],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}[✓]{Colors.ENDC} {package} installed successfully")
            else:
                print(f"{Colors.RED}[✗]{Colors.ENDC} Failed to install {package}")
                print(f"{Colors.YELLOW}Error: {result.stderr[:200]}{Colors.ENDC}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[✗]{Colors.ENDC} Installation timeout for {package}")
            return False
        except Exception as e:
            print(f"{Colors.RED}[✗]{Colors.ENDC} Error installing {package}: {e}")
            return False
    
    print(f"\n{Colors.GREEN}[✓] All dependencies installed!{Colors.ENDC}")
    print(f"{Colors.CYAN}Please restart Webber to continue.{Colors.ENDC}\n")
    return False  # Return False to restart

# Try importing after potential installation
try:
    import requests
    from bs4 import BeautifulSoup
    import psutil
    DEPENDENCIES_OK = True
except ImportError:
    DEPENDENCIES_OK = False

# Detect environment
IS_TERMUX = os.path.exists('/data/data/com.termux')
IS_ANDROID = 'ANDROID_ROOT' in os.environ or IS_TERMUX
PLATFORM = platform.system()

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Global state
webber_state = {
    'running': False,
    'stats': {
        'cycles': 0,
        'total_visits': 0,
        'total_pages': 0,
        'total_time': 0,
        'unique_sessions': 0,
        'natural_behaviors': 0,
        'bans_avoided': 0
    },
    'config': {},
    'start_time': None
}

stop_flag = False

def print_banner():
    """Display ASCII art banner"""
    banner = f"""{Colors.CYAN}
    ╦ ╦╔═╗╔╗ ╔╗ ╔═╗╦═╗
    ║║║║╣ ╠╩╗╠╩╗║╣ ╠╦╝
    ╚╩╝╚═╝╚═╝╚═╝╚═╝╩╚═
    {Colors.ENDC}{Colors.BOLD}Advanced Web Traffic Simulator{Colors.ENDC}
    {Colors.YELLOW}v4.0 - Ethical Testing Edition{Colors.ENDC}
    """
    print(banner)

def detect_hardware_capacity():
    """Auto-detect device capabilities and set appropriate limits"""
    try:
        cpu_count = psutil.cpu_count(logical=True)
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        # Categorize device
        if IS_TERMUX or IS_ANDROID:
            device_class = "mobile"
            if ram_gb < 2:
                capacity = "low"
            elif ram_gb < 4:
                capacity = "medium"
            else:
                capacity = "high"
        else:
            device_class = "desktop"
            if ram_gb < 4:
                capacity = "low"
            elif ram_gb < 8:
                capacity = "medium"
            elif ram_gb < 16:
                capacity = "high"
            else:
                capacity = "ultra"
        
        # Set capacity parameters
        capacity_map = {
            "low": {
                "max_concurrent": 1,
                "visits_per_cycle": (2, 4),
                "max_pages_per_visit": 3,
                "delay_multiplier": 1.5
            },
            "medium": {
                "max_concurrent": 2,
                "visits_per_cycle": (3, 6),
                "max_pages_per_visit": 5,
                "delay_multiplier": 1.0
            },
            "high": {
                "max_concurrent": 3,
                "visits_per_cycle": (4, 8),
                "max_pages_per_visit": 7,
                "delay_multiplier": 0.8
            },
            "ultra": {
                "max_concurrent": 4,
                "visits_per_cycle": (5, 10),
                "max_pages_per_visit": 10,
                "delay_multiplier": 0.6
            }
        }
        
        config = capacity_map[capacity]
        
        return {
            "device_class": device_class,
            "capacity": capacity,
            "cpu_count": cpu_count,
            "ram_gb": round(ram_gb, 1),
            "platform": PLATFORM,
            **config
        }
        
    except Exception:
        # Fallback to safe defaults
        return {
            "device_class": "unknown",
            "capacity": "low",
            "cpu_count": 1,
            "ram_gb": 1.0,
            "platform": PLATFORM,
            "max_concurrent": 1,
            "visits_per_cycle": (2, 3),
            "max_pages_per_visit": 3,
            "delay_multiplier": 1.5
        }

def print_system_info():
    """Display detected system information"""
    hw = detect_hardware_capacity()
    
    print(f"\n{Colors.HEADER}═══ SYSTEM DETECTION ═══{Colors.ENDC}")
    print(f"{Colors.CYAN}Platform:{Colors.ENDC} {hw['platform']}")
    print(f"{Colors.CYAN}Device Class:{Colors.ENDC} {hw['device_class'].upper()}")
    print(f"{Colors.CYAN}CPU Cores:{Colors.ENDC} {hw['cpu_count']}")
    print(f"{Colors.CYAN}RAM:{Colors.ENDC} {hw['ram_gb']} GB")
    print(f"{Colors.CYAN}Capacity:{Colors.ENDC} {hw['capacity'].upper()}")
    print(f"{Colors.CYAN}Max Concurrent:{Colors.ENDC} {hw['max_concurrent']}")
    print(f"{Colors.CYAN}Visits/Cycle:{Colors.ENDC} {hw['visits_per_cycle'][0]}-{hw['visits_per_cycle'][1]}")
    print(f"{Colors.CYAN}Max Pages/Visit:{Colors.ENDC} {hw['max_pages_per_visit']}")
    
    if IS_TERMUX:
        print(f"{Colors.YELLOW}⚡ Termux environment detected - optimized for mobile{Colors.ENDC}")
    
    return hw

def load_keywords(wordlist_path):
    """Load keywords from wordlist file"""
    if not os.path.exists(wordlist_path):
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} Wordlist not found: {wordlist_path}")
        return None
    
    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not keywords:
            print(f"{Colors.RED}[ERROR]{Colors.ENDC} Wordlist is empty")
            return None
        
        print(f"{Colors.GREEN}[✓]{Colors.ENDC} Loaded {len(keywords)} keywords from wordlist")
        return keywords
        
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} Failed to load wordlist: {e}")
        return None

def get_ethical_consent():
    """Get user consent for ethical usage"""
    print(f"\n{Colors.HEADER}═══ ETHICAL USAGE AGREEMENT ═══{Colors.ENDC}")
    print(f"{Colors.YELLOW}This tool is designed for:{Colors.ENDC}")
    print("  • Authorized penetration testing (HTB, CTF)")
    print("  • Testing your own websites")
    print("  • Security research with permission")
    print("  • Educational purposes in controlled environments")
    
    print(f"\n{Colors.RED}You must NOT use this tool to:{Colors.ENDC}")
    print("  ✗ Attack websites without authorization")
    print("  ✗ Manipulate metrics fraudulently")
    print("  ✗ Violate Terms of Service")
    print("  ✗ Conduct malicious activities")
    
    print(f"\n{Colors.BOLD}By using Webber, you agree that:{Colors.ENDC}")
    print("  1. You have explicit authorization to test the target")
    print("  2. You will use this tool ethically and legally")
    print("  3. You accept full responsibility for your actions")
    print("  4. You will respect rate limits and robots.txt")
    
    consent = input(f"\n{Colors.CYAN}Do you agree to use Webber ethically? (yes/no): {Colors.ENDC}").strip().lower()
    
    if consent != 'yes':
        print(f"{Colors.RED}[!] Consent not given. Exiting.{Colors.ENDC}")
        return False
    
    return True

def verify_target_authorization(target_url):
    """Verify user has authorization for target"""
    print(f"\n{Colors.HEADER}═══ TARGET AUTHORIZATION ═══{Colors.ENDC}")
    print(f"{Colors.CYAN}Target URL:{Colors.ENDC} {target_url}")
    print(f"\n{Colors.YELLOW}IMPORTANT:{Colors.ENDC} You must have explicit permission to test this target.")
    print("This includes:")
    print("  • HTB/CTF challenge boxes")
    print("  • Your own websites")
    print("  • Sites with written authorization")
    print("  • Test environments you control")
    
    confirm = input(f"\n{Colors.CYAN}Do you have authorization to test this target? (yes/no): {Colors.ENDC}").strip().lower()
    
    if confirm != 'yes':
        print(f"{Colors.RED}[!] Target authorization not confirmed. Exiting.{Colors.ENDC}")
        return False
    
    return True

def check_robots_txt(target_url, mode='check'):
    """Check and respect robots.txt based on mode"""
    try:
        parsed = urlparse(target_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        if mode == 'ignore':
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} Skipping robots.txt check (ignore mode)")
            return True
        
        print(f"{Colors.CYAN}[i] Checking robots.txt...{Colors.ENDC}")
        
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            print(f"{Colors.GREEN}[✓]{Colors.ENDC} Found robots.txt")
            
            # Check for restrictive rules
            if 'Disallow: /' in response.text:
                print(f"{Colors.YELLOW}[!]{Colors.ENDC} robots.txt disallows crawling")
                
                if mode == 'respect':
                    print(f"{Colors.RED}[!]{Colors.ENDC} Respect mode enabled - cannot proceed")
                    return False
                elif mode == 'check':
                    print(f"{Colors.CYAN}Note:{Colors.ENDC} You can override this for authorized testing (HTB/CTF)")
                    respect = input(f"{Colors.CYAN}Continue anyway? (yes/no): {Colors.ENDC}").strip().lower()
                    return respect == 'yes'
            else:
                print(f"{Colors.GREEN}[✓]{Colors.ENDC} No restrictive crawling rules found")
        else:
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} No robots.txt found (proceeding)")
        
        return True
        
    except Exception:
        print(f"{Colors.YELLOW}[!]{Colors.ENDC} Could not check robots.txt (proceeding)")
        return True


class BehaviorRandomizer:
    """Generates realistic human behavior patterns"""
    
    @staticmethod
    def random_reading_speed():
        reading_styles = [150, 200, 250, 300, 350, 400, 500, 600]
        return random.choice(reading_styles)
    
    @staticmethod
    def random_attention_span():
        attention_profiles = [
            ('impatient', 0.3, 0.6),
            ('casual', 0.5, 1.0),
            ('interested', 0.8, 1.5),
            ('thorough', 1.2, 2.0),
            ('researcher', 1.5, 3.0)
        ]
        profile = random.choice(attention_profiles)
        return profile[0], random.uniform(profile[1], profile[2])
    
    @staticmethod
    def random_navigation_pattern():
        patterns = ['linear', 'scanner', 'explorer', 'focused', 'wanderer']
        return random.choice(patterns)
    
    @staticmethod
    def should_make_mistake():
        return random.random() < 0.15


class RateLimiter:
    def __init__(self, hw_config):
        multiplier = hw_config['delay_multiplier']
        self.max_requests = int(random.randint(5, 15) * multiplier)
        self.time_window = random.randint(45, 90)
        self.requests = deque()
        self.aggressive_mode = random.random() < 0.3
    
    def wait_if_needed(self):
        now = time.time()
        
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        if len(self.requests) >= self.max_requests:
            base_wait = self.time_window - (now - self.requests[0])
            sleep_time = base_wait * (random.uniform(0.5, 0.8) if self.aggressive_mode else random.uniform(1.0, 2.5))
            
            if sleep_time > 0:
                time.sleep(sleep_time)
                if random.random() < 0.5:
                    self.requests.clear()
        
        self.requests.append(now)


class WebberBot:
    def __init__(self, hw_config, keywords, target_url, use_proxies=True):
        self.hw_config = hw_config
        self.keywords = keywords
        self.target_url = target_url
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(hw_config)
        
        # IP and device spoofing enabled by default
        self.use_proxies = use_proxies
        self.proxy_pool = []
        self.current_proxy = None
        
        # Randomize device type for this session
        self.is_mobile = random.random() < 0.65
        self.behavior_profile = BehaviorRandomizer.random_navigation_pattern()
        self.session_id = str(uuid.uuid4())
        
        # Device fingerprint randomization
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # Load proxy pool if available
        if self.use_proxies:
            self._load_proxy_pool()
        
        self.user_agents = self._get_user_agents()
        self.update_headers()
    
    def _generate_device_fingerprint(self):
        """Generate unique device fingerprint for this session"""
        screen_resolutions = {
            'mobile': [
                (360, 640), (375, 667), (390, 844), (393, 851),
                (412, 915), (414, 896), (428, 926)
            ],
            'desktop': [
                (1366, 768), (1440, 900), (1536, 864), (1920, 1080),
                (2560, 1440), (3840, 2160)
            ]
        }
        
        device_type = 'mobile' if self.is_mobile else 'desktop'
        screen = random.choice(screen_resolutions[device_type])
        
        return {
            'screen_width': screen[0],
            'screen_height': screen[1],
            'color_depth': random.choice([24, 32]),
            'timezone_offset': random.choice([-480, -420, -360, -300, -240, -180, 0, 60, 120, 180, 240, 300, 360, 420, 480, 540]),
            'language': random.choice(['en-US', 'en-GB', 'en-CA', 'en-AU']),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64', 'iPhone', 'Android']),
            'hardware_concurrency': random.choice([2, 4, 6, 8, 12, 16]),
            'device_memory': random.choice([2, 4, 8, 16, 32]),
            'do_not_track': random.choice(['1', None, 'unspecified'])
        }
    
    def _load_proxy_pool(self):
        """Load proxy pool from multiple sources"""
        sources = []
        
        # Source 1: Environment variable
        proxy_env = os.environ.get('PROXY_LIST', '')
        if proxy_env:
            sources.extend([p.strip() for p in proxy_env.split(',') if p.strip()])
        
        # Source 2: proxies.txt file
        if os.path.exists('proxies.txt'):
            try:
                with open('proxies.txt', 'r') as f:
                    sources.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
            except:
                pass
        
        # Source 3: Auto-fetch free proxies if none available
        if not sources:
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} No proxies found in proxies.txt or environment")
            print(f"{Colors.CYAN}[*]{Colors.ENDC} Fetching free proxies automatically...")
            sources = self._fetch_free_proxies()
            
            if sources:
                # Save to proxies.txt for future use
                try:
                    with open('proxies.txt', 'w') as f:
                        f.write("# Auto-fetched free proxies\n")
                        f.write("# Add your own proxies here for better reliability\n\n")
                        for proxy in sources:
                            f.write(f"{proxy}\n")
                    print(f"{Colors.GREEN}[✓]{Colors.ENDC} Saved proxies to proxies.txt")
                except:
                    pass
        
        if sources:
            self.proxy_pool = sources
            random.shuffle(self.proxy_pool)
            print(f"{Colors.GREEN}[✓]{Colors.ENDC} Loaded {len(self.proxy_pool)} proxies for IP rotation")
        else:
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} No proxies available - using direct connection")
            print(f"{Colors.CYAN}[i]{Colors.ENDC} Device spoofing is still active (different user agents & headers)")
    
    def _fetch_free_proxies(self):
        """Fetch free proxies from public sources"""
        proxies = []
        
        print(f"{Colors.CYAN}[*]{Colors.ENDC} Fetching from free proxy sources...")
        
        # Source 1: ProxyScrape API
        try:
            url = "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                proxy_list = response.text.strip().split('\n')
                for proxy in proxy_list[:10]:  # Take first 10
             
