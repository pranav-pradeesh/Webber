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
                    if proxy.strip():
                        proxies.append(f"http://{proxy.strip()}")
                print(f"{Colors.GREEN}[✓]{Colors.ENDC} ProxyScrape: {len(proxies)} proxies")
        except Exception as e:
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} ProxyScrape failed: {str(e)[:50]}")
        
        # Source 2: Proxy-List.download
        try:
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                proxy_list = response.text.strip().split('\n')
                count_before = len(proxies)
                for proxy in proxy_list[:10]:
                    if proxy.strip() and proxy.strip() not in [p.replace('http://', '') for p in proxies]:
                        proxies.append(f"http://{proxy.strip()}")
                added = len(proxies) - count_before
                print(f"{Colors.GREEN}[✓]{Colors.ENDC} Proxy-List: {added} new proxies")
        except Exception as e:
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} Proxy-List failed: {str(e)[:50]}")
        
        # Source 3: GeoNode API
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=10&page=1&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                count_before = len(proxies)
                for proxy_data in data.get('data', []):
                    ip = proxy_data.get('ip')
                    port = proxy_data.get('port')
                    if ip and port:
                        proxy_str = f"http://{ip}:{port}"
                        if proxy_str not in proxies:
                            proxies.append(proxy_str)
                added = len(proxies) - count_before
                print(f"{Colors.GREEN}[✓]{Colors.ENDC} GeoNode: {added} new proxies")
        except Exception as e:
            print(f"{Colors.YELLOW}[!]{Colors.ENDC} GeoNode failed: {str(e)[:50]}")
        
        if proxies:
            print(f"{Colors.GREEN}[✓]{Colors.ENDC} Total fetched: {len(proxies)} working proxies")
        else:
            print(f"{Colors.RED}[!]{Colors.ENDC} Failed to fetch proxies from all sources")
        
        return proxies
    
    def _get_random_proxy(self):
        """Get random proxy from pool"""
        if not self.proxy_pool:
            return None
        
        # Random selection (not sequential)
        proxy_url = random.choice(self.proxy_pool)
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def _rotate_identity(self):
        """Rotate complete identity - IP, device, headers"""
        # Rotate proxy (IP address)
        if self.use_proxies and self.proxy_pool:
            self.current_proxy = self._get_random_proxy()
            webber_state['stats']['ip_rotations'] = webber_state['stats'].get('ip_rotations', 0) + 1
        
        # Generate new device fingerprint
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # Randomize device type
        self.is_mobile = random.random() < 0.65
        
        # Update behavior profile
        self.behavior_profile = BehaviorRandomizer.random_navigation_pattern()
        
        # Regenerate user agents
        self.user_agents = self._get_user_agents()
        
        # Update headers with new fingerprint
        self.update_headers()
        
        # Sometimes create new session (clears cookies)
        if random.random() > 0.5:
            self.session = requests.Session()
            self.update_headers()
            webber_state['stats']['unique_sessions'] += 1
        
        webber_state['stats']['identity_rotations'] = webber_state['stats'].get('identity_rotations', 0) + 1
    
    def _get_user_agents(self):
        mobile = [
            # iPhone variants
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1',
            
            # Samsung devices
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.116 Mobile Safari/537.36',
            
            # Google Pixel
            'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36',
            
            # iPad
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            
            # OnePlus
            'Mozilla/5.0 (Linux; Android 13; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36',
            
            # Xiaomi
            'Mozilla/5.0 (Linux; Android 13; 2211133C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.116 Mobile Safari/537.36',
        ]
        
        desktop = [
            # Windows Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            
            # Windows Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            
            # Windows Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.144',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.83',
            
            # macOS Chrome
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # macOS Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            
            # macOS Firefox
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
        ]
        
        return mobile if self.is_mobile else desktop
    
    def update_headers(self):
        user_agent = random.choice(self.user_agents)
        fp = self.device_fingerprint
        
        # Base headers with device fingerprinting
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': f"{fp['language']},en;q=0.9",
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add device-specific headers
        if random.random() > 0.4:
            headers['Sec-Ch-Ua'] = f'"Chromium";v="120", "Not_A Brand";v="8"'
            headers['Sec-Ch-Ua-Platform'] = f'"{fp["platform"]}"'
        
        if self.is_mobile and random.random() > 0.5:
            headers['Sec-Ch-Ua-Mobile'] = '?1'
            headers['Viewport-Width'] = str(fp['screen_width'])
        
        # Random additional headers
        if random.random() > 0.6:
            headers['DNT'] = fp['do_not_track'] if fp['do_not_track'] else '1'
        
        if random.random() > 0.5:
            headers['Sec-Fetch-Dest'] = 'document'
            headers['Sec-Fetch-Mode'] = 'navigate'
            headers['Sec-Fetch-Site'] = random.choice(['none', 'same-origin', 'cross-site'])
        
        # X-Forwarded-For header spoofing (makes it look like different IPs)
        if random.random() > 0.3:
            headers['X-Forwarded-For'] = self._generate_fake_ip()
        
        # Via header (simulate proxy chain)
        if random.random() > 0.7:
            headers['Via'] = f'1.1 proxy{random.randint(1,999)}.example.com'
        
        self.session.headers.update(headers)
    
    def _generate_fake_ip(self):
        """Generate realistic-looking IP address"""
        # Common IP ranges for different regions
        ip_ranges = [
            # US ranges
            lambda: f"{random.choice([24, 66, 173, 192, 198])}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            # Europe ranges
            lambda: f"{random.choice([80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90])}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            # Asia ranges
            lambda: f"{random.choice([103, 110, 111, 112, 113, 114, 115, 116, 117, 118])}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
        ]
        
        return random.choice(ip_ranges)()
    
    def intelligent_delay(self, min_base=1, max_base=5):
        _, attention = BehaviorRandomizer.random_attention_span()
        delay = random.uniform(min_base, max_base) * attention * self.hw_config['delay_multiplier']
        
        if random.random() > 0.92:
            delay += random.uniform(5, 15)
        
        delay = max(0.5, delay)
        time.sleep(delay)
    
    def make_request(self, url, **kwargs):
        self.rate_limiter.wait_if_needed()
        
        if 'timeout' not in kwargs:
            kwargs['timeout'] = random.randint(10, 20)
        
        # Use proxy if available
        if self.use_proxies and self.current_proxy:
            kwargs['proxies'] = self.current_proxy
        
        max_retries = 3
        for retry in range(max_retries):
            try:
                response = self.session.request('GET', url, **kwargs)
                
                if response.status_code == 429:
                    wait = int(response.headers.get('Retry-After', 60))
                    time.sleep(wait + random.uniform(5, 15))
                    continue
                
                # Success - proxy is working
                return response
                
            except Exception as e:
                # Proxy might be dead, try rotating
                if self.use_proxies and self.proxy_pool and 'ProxyError' in str(type(e).__name__):
                    print(f"{Colors.YELLOW}[!]{Colors.ENDC} Proxy failed, rotating...")
                    self.current_proxy = self._get_random_proxy()
                
                if retry < max_retries - 1:
                    time.sleep((2 ** retry) * random.uniform(2, 5))
                else:
                    return None
        
        return None
    
    def search_and_click(self, query):
        try:
            self.intelligent_delay(1, 3)
            
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            response = self.make_request(search_url)
            
            if response and response.status_code == 200:
                self.intelligent_delay(2, 5)
                return True
            
            return False
            
        except Exception:
            return False
    
    def visit_page(self, url):
        page_data = {
            'pages_visited': 0,
            'duration': 0,
            'links_clicked': []
        }
        
        try:
            start = time.time()
            response = self.make_request(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                text = soup.get_text()
                words = len(text.split())
                
                wpm = BehaviorRandomizer.random_reading_speed()
                read_time = (words / wpm) * 60
                read_time = max(15, min(120, read_time))
                
                time.sleep(read_time)
                page_data['pages_visited'] += 1
                
                # Visit internal pages
                links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href and (href.startswith('/') or url in href):
                        full_url = urljoin(url, href)
                        if full_url not in links and full_url != url:
                            links.append(full_url)
                
                max_pages = self.hw_config['max_pages_per_visit']
                pages_to_visit = min(len(links), random.randint(2, max_pages))
                
                for i in range(pages_to_visit):
                    if stop_flag or i >= len(links):
                        break
                    
                    self.intelligent_delay(2, 8)
                    
                    try:
                        resp = self.make_request(links[i])
                        if resp and resp.status_code == 200:
                            page_data['pages_visited'] += 1
                            page_data['links_clicked'].append(links[i])
                            time.sleep(random.uniform(10, 40))
                    except:
                        pass
                
                page_data['duration'] = time.time() - start
                webber_state['stats']['bans_avoided'] += 1
                
        except Exception:
            pass
        
        return page_data
    
    def simulate_visits(self, num_visits):
        all_visits = []
        
        for visit_num in range(num_visits):
            if stop_flag:
                break
            
            # Rotate identity every 2-3 visits (appears as different users/IPs)
            if visit_num > 0 and visit_num % random.randint(2, 3) == 0:
                self._rotate_identity()
                time.sleep(random.uniform(1, 3))
            
            # Search traffic
            if random.random() > 0.35 and self.keywords:
                keyword = random.choice(self.keywords)
                self.search_and_click(keyword)
            
            # Visit site
            visit_data = self.visit_page(self.target_url)
            all_visits.append(visit_data)
            
            webber_state['stats']['total_visits'] += 1
            webber_state['stats']['total_pages'] += visit_data['pages_visited']
            webber_state['stats']['total_time'] += visit_data['duration']
            
            # Delay between visits
            if visit_num < num_visits - 1:
                delay = random.uniform(30, 120) * self.hw_config['delay_multiplier']
                time.sleep(delay)
        
        return all_visits


def print_progress():
    """Print live progress statistics"""
    while webber_state['running']:
        os.system('clear' if os.name != 'nt' else 'cls')
        print_banner()
        
        stats = webber_state['stats']
        elapsed = int(time.time() - webber_state['start_time']) if webber_state['start_time'] else 0
        
        print(f"{Colors.HEADER}═══ LIVE STATISTICS ═══{Colors.ENDC}")
        print(f"{Colors.CYAN}Runtime:{Colors.ENDC} {elapsed}s")
        print(f"{Colors.CYAN}Cycles:{Colors.ENDC} {stats['cycles']}")
        print(f"{Colors.GREEN}Total Visits:{Colors.ENDC} {stats['total_visits']}")
        print(f"{Colors.GREEN}Pages Viewed:{Colors.ENDC} {stats['total_pages']}")
        print(f"{Colors.YELLOW}Time Spent:{Colors.ENDC} {int(stats['total_time'] / 60)}m")
        print(f"{Colors.BLUE}Unique Sessions:{Colors.ENDC} {stats['unique_sessions']}")
        print(f"{Colors.CYAN}Natural Behaviors:{Colors.ENDC} {stats['natural_behaviors']}")
        print(f"{Colors.GREEN}Bans Avoided:{Colors.ENDC} {stats['bans_avoided']}")
        print(f"{Colors.MAGENTA}Identity Rotations:{Colors.ENDC} {stats.get('identity_rotations', 0)}")
        print(f"{Colors.MAGENTA}IP Rotations:{Colors.ENDC} {stats.get('ip_rotations', 0)}")
        
        # Show proxy pool size
        proxy_count = stats.get('proxy_pool_size', 0)
        if proxy_count > 0:
            print(f"{Colors.CYAN}Proxy Pool:{Colors.ENDC} {proxy_count} active")
        
        avg_pages = stats['total_pages'] / max(stats['total_visits'], 1)
        print(f"{Colors.YELLOW}Avg Pages/Visit:{Colors.ENDC} {avg_pages:.1f}")
        
        print(f"\n{Colors.GREEN}✓ Requests appear from different devices & IPs{Colors.ENDC}")
        print(f"{Colors.RED}Press Ctrl+C to stop{Colors.ENDC}")
        
        time.sleep(2)


def run_webber(config):
    """Main Webber execution loop"""
    global stop_flag, webber_state
    
    webber_state['running'] = True
    webber_state['start_time'] = time.time()
    webber_state['config'] = config
    
    hw = config['hw_config']
    keywords = config['keywords']
    target = config['target_url']
    
    # Start progress display
    progress_thread = threading.Thread(target=print_progress, daemon=True)
    progress_thread.start()
    
    try:
        while not stop_flag:
            webber_state['stats']['cycles'] += 1
            
            # Create bot instance (will auto-fetch proxies on first run)
            bot = WebberBot(hw, keywords, target)
            webber_state['stats']['unique_sessions'] += 1
            
            # Store proxy pool size for display
            webber_state['stats']['proxy_pool_size'] = len(bot.proxy_pool)
            
            # Determine visits for this cycle
            min_v, max_v = hw['visits_per_cycle']
            num_visits = random.randint(min_v, max_v)
            
            # Run visits
            bot.simulate_visits(num_visits)
            
            # Cycle delay
            if not stop_flag:
                delay = random.randint(300, 900)
                time.sleep(delay)
        
    except KeyboardInterrupt:
        pass
    finally:
        webber_state['running'] = False
        print(f"\n{Colors.GREEN}[✓] Webber stopped gracefully{Colors.ENDC}")


def main():
    """Main CLI entry point"""
    
    # Check dependencies first (before showing banner)
    if not DEPENDENCIES_OK:
        if not check_and_install_dependencies():
            sys.exit(1)
        else:
            print(f"\n{Colors.GREEN}Please restart Webber now.{Colors.ENDC}")
            sys.exit(0)
    
    parser = argparse.ArgumentParser(
        description='Webber - Advanced Web Traffic Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard HTB testing (asks about robots.txt)
  webber --target https://example.com --wordlist keywords.txt
  
  # Ignore robots.txt for HTB/CTF (authorized testing)
  webber -t https://example.com -w keywords.txt --robots-mode ignore
  
  # Enforce robots.txt compliance (production testing)
  webber -t https://example.com -w keywords.txt --robots-mode respect
  
  # Quick mode (skip all prompts, ignore robots.txt)
  webber -t https://example.com -w keywords.txt --no-consent --robots-mode ignore
        """
    )
    
    parser.add_argument('-t', '--target', required=True, help='Target URL to test')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to keyword wordlist')
    parser.add_argument('--no-consent', action='store_true', help='Skip consent prompts (use with caution)')
    parser.add_argument('--robots-mode', choices=['check', 'respect', 'ignore'], default='check',
                       help='robots.txt handling: check (ask), respect (enforce), ignore (skip check)')
    
    args = parser.parse_args()
    
    # Show banner after dependency check
    print_banner()
    
    # Check dependencies
    if not DEPENDENCIES_OK:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} Missing dependencies!")
        print("Install: pip install requests beautifulsoup4 psutil")
        sys.exit(1)
    
    # Detect hardware
    hw_config = print_system_info()
    
    # Load wordlist
    keywords = load_keywords(args.wordlist)
    if keywords is None:
        sys.exit(1)
    
    # Ethical consent
    if not args.no_consent:
        if not get_ethical_consent():
            sys.exit(1)
        
        if not verify_target_authorization(args.target):
            sys.exit(1)
        
        if not check_robots_txt(args.target, args.robots_mode):
            sys.exit(1)
    else:
        # Even with --no-consent, still check robots.txt unless ignore mode
        if args.robots_mode != 'ignore':
            if not check_robots_txt(args.target, args.robots_mode):
                sys.exit(1)
    
    # Final confirmation
    print(f"\n{Colors.HEADER}═══ READY TO START ═══{Colors.ENDC}")
    print(f"{Colors.CYAN}Target:{Colors.ENDC} {args.target}")
    print(f"{Colors.CYAN}Keywords:{Colors.ENDC} {len(keywords)} loaded")
    print(f"{Colors.CYAN}Device Capacity:{Colors.ENDC} {hw_config['capacity'].upper()}")
    
    input(f"\n{Colors.GREEN}Press ENTER to start Webber...{Colors.ENDC}")
    
    # Configure and run
    config = {
        'hw_config': hw_config,
        'keywords': keywords,
        'target_url': args.target
    }
    
    try:
        run_webber(config)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Interrupted by user{Colors.ENDC}")
    finally:
        # Final stats
        stats = webber_state['stats']
        print(f"\n{Colors.HEADER}═══ FINAL STATISTICS ═══{Colors.ENDC}")
        print(f"Total Cycles: {stats['cycles']}")
        print(f"Total Visits: {stats['total_visits']}")
        print(f"Total Pages: {stats['total_pages']}")
        print(f"Time Spent: {int(stats['total_time'] / 60)} minutes")
        print(f"Total Unique Sessions: {stats['unique_sessions']}")
        print(f"Identity Rotations: {stats.get('identity_rotations', 0)}")
        print(f"IP Rotations: {stats.get('ip_rotations', 0)}")
        print(f"{Colors.GREEN}Thank you for using Webber ethically!{Colors.ENDC}\n")


if __name__ == "__main__":
    main()

