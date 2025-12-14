# 🕷️ WEBBER - Advanced Web Traffic Simulator

```
    ╦ ╦╔═╗╔╗ ╔╗ ╔═╗╦═╗
    ║║║║╣ ╠╩╗╠╩╗║╣ ╠╦╝
    ╚╩╝╚═╝╚═╝╚═╝╚═╝╩╚═
    Advanced Web Traffic Simulator
    v4.0 - Ethical Testing Edition
```

**Realistic web traffic simulation for HTB/CTF challenges and authorized penetration testing.**

---

## ⚡ Quick Start (One Command!)

```bash
# Download and run - everything installs automatically!
python3 webber.py -t https://target.htb -w keywords.txt
```

That's it! Webber will:
- ✅ Auto-install all dependencies
- ✅ Auto-fetch free proxies
- ✅ Auto-configure everything
- ✅ Start simulating traffic

---

## 📦 Installation

### All Platforms (Linux, macOS, Windows, Termux)

**Step 1:** Download Webber
```bash
# Option 1: Direct download
wget https://your-link/webber.py

# Option 2: Git clone
git clone https://your-repo/webber.git
cd webber
```

**Step 2:** Create a keyword wordlist
```bash
# Create keywords.txt
cat > keywords.txt << EOF
target system name
admin portal
login page
user dashboard
EOF
```

**Step 3:** Run (auto-installs everything!)
```bash
python3 webber.py -t https://target.htb -w keywords.txt
```

**First run will:**
1. Detect missing dependencies
2. Ask permission to install them
3. Auto-fetch 20+ free proxies
4. Configure everything automatically
5. Start traffic simulation

---

## 🎯 Features

### 🤖 Automatic by Default
- **Device Spoofing**: 30+ different devices (iPhone, Android, Windows, Mac)
- **IP Rotation**: Auto-fetches and rotates through free proxies
- **Fingerprinting**: Unique browser fingerprints per session
- **Human Behavior**: Reading patterns, mistakes, distractions
- **Smart Delays**: Realistic timing based on content

### 🛡️ Stealth Features
- ✅ Different user agents per request
- ✅ Randomized device fingerprints
- ✅ Spoofed IP headers (X-Forwarded-For)
- ✅ Automatic proxy rotation (20+ free proxies)
- ✅ Session identity changes every 2-3 visits
- ✅ Natural browsing patterns
- ✅ Human mistakes (typos, back button)
- ✅ Hardware-optimized performance

### 🔧 Hardware Auto-Detection
Automatically detects your device and optimizes:
- **Mobile/Termux**: Low-power mode
- **Desktop (4GB RAM)**: Medium capacity
- **Desktop (8GB+ RAM)**: High performance
- **Workstation (16GB+ RAM)**: Maximum capacity

### 📊 Live Statistics Dashboard
```
═══ LIVE STATISTICS ═══
Runtime: 156s
Cycles: 3
Total Visits: 18
Pages Viewed: 87
Time Spent: 45m
Unique Sessions: 18
Identity Rotations: 6
IP Rotations: 6
Proxy Pool: 23 active

✓ Requests appear from different devices & IPs
```

---

## 🚀 Usage

### Basic Usage
```bash
# Simple mode (auto-install, auto-proxies)
python3 webber.py -t https://target.htb -w keywords.txt
```

### HTB/CTF Quick Mode
```bash
# Skip all prompts, ignore robots.txt
python3 webber.py -t https://target.htb -w keywords.txt --no-consent --robots-mode ignore
```

### Production Testing Mode
```bash
# Respects robots.txt, asks permissions
python3 webber.py -t https://client-site.com -w keywords.txt --robots-mode respect
```

### Advanced Options
```bash
# Full control
python3 webber.py \
  --target https://target.htb \
  --wordlist keywords.txt \
  --robots-mode ignore \
  --no-consent
```

---

## 📝 Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--target` | `-t` | Target URL to test | Required |
| `--wordlist` | `-w` | Path to keyword file | Required |
| `--robots-mode` | - | `check`, `respect`, or `ignore` | `check` |
| `--no-consent` | - | Skip ethical consent prompts | Off |

### Robots.txt Modes

- **check** (default): Asks if you want to proceed when restrictions found
- **respect**: Enforces robots.txt compliance, stops if disallowed
- **ignore**: Skips robots.txt check entirely (HTB/CTF mode)

---

## 📄 Creating a Wordlist

Create `keywords.txt` with your target-specific keywords:

```text
# HTB Target Keywords
target machine name
admin panel
login portal
user dashboard
system console

# Lines starting with # are comments (ignored)
```

**Tips:**
- Use 5-20 keywords
- Include variations (with/without spaces)
- Add common terms for the target
- Mix general and specific queries

---

## 🌐 Proxy System

### Automatic Proxy Setup (Default)

Webber **automatically fetches 20+ free proxies** on first run:

```
[*] Fetching free proxies...
[✓] Fetched 23 working proxies
[✓] Saved to proxies.txt
[✓] Proxy rotation enabled
```

Proxies are automatically:
- ✅ Fetched from multiple sources
- ✅ Tested for connectivity
- ✅ Saved to `proxies.txt`
- ✅ Rotated randomly during traffic simulation
- ✅ Re-fetched if none are working

### Manual Proxy Setup (Optional)

If you have your own proxies, create `proxies.txt`:

```text
# Your custom proxies
http://proxy1.example.com:8080
http://username:password@proxy2.example.com:8080
socks5://proxy3.example.com:1080

# Free proxies
http://123.45.67.89:8080
http://98.76.54.32:3128
```

**Format:** `protocol://[username:password@]host:port`

Or use environment variable:
```bash
export PROXY_LIST="http://proxy1.com:8080,http://proxy2.com:8080"
```

---

## 🔧 What Gets Randomized

### Device Fingerprints (Automatic)
- **User Agent**: 30+ real devices
- **Screen Resolution**: Mobile (360x640 to 428x926), Desktop (1366x768 to 3840x2160)
- **Color Depth**: 24-bit or 32-bit
- **Timezone**: Global offsets (-480 to +540)
- **Language**: en-US, en-GB, en-CA, en-AU
- **Platform**: Win32, MacIntel, Linux x86_64, iPhone, Android
- **CPU Cores**: 2, 4, 6, 8, 12, 16
- **Device Memory**: 2GB, 4GB, 8GB, 16GB, 32GB

### Network Spoofing
- **X-Forwarded-For**: Fake IPs from US, EU, Asia ranges
- **Via Header**: Simulated proxy chains
- **Real IP**: Rotates through proxy pool

### Human Behavior
- **Reading Speed**: 150-600 words per minute
- **Attention Span**: Impatient → Researcher (0.3x to 3.0x)
- **Navigation Pattern**: Linear, scanner, explorer, focused, wanderer
- **Mistakes**: 15% chance of typos, back button, refresh
- **Distractions**: 8% chance of 5-30s pause

---

## 🖥️ Platform Support

### ✅ Linux
```bash
# Auto-installs dependencies
python3 webber.py -t https://target.htb -w keywords.txt
```

### ✅ macOS
```bash
# Works out of the box
python3 webber.py -t https://target.htb -w keywords.txt
```

### ✅ Windows
```bash
# Use Python 3
python webber.py -t https://target.htb -w keywords.txt
```

### ✅ Termux (Android)
```bash
# Install Python first
pkg install python

# Run Webber
python webber.py -t https://target.htb -w keywords.txt
```

---

## 📊 Example Session

```bash
$ python3 webber.py -t https://target.htb -w keywords.txt

    ╦ ╦╔═╗╔╗ ╔╗ ╔═╗╦═╗
    ║║║║╣ ╠╩╗╠╩╗║╣ ╠╦╝
    ╚╩╝╚═╝╚═╝╚═╝╚═╝╩╚═
    Advanced Web Traffic Simulator
    v4.0 - Ethical Testing Edition

[*] Checking dependencies...
[✓] All dependencies installed

═══ SYSTEM DETECTION ═══
Platform: Linux
Device Class: DESKTOP
CPU Cores: 8
RAM: 16.0 GB
Capacity: HIGH
Max Concurrent: 3
Visits/Cycle: 4-8
Max Pages/Visit: 7

[✓] Loaded 15 keywords from wordlist

[*] Fetching free proxies...
[✓] Fetched 23 working proxies
[✓] Saved to proxies.txt

═══ ETHICAL USAGE AGREEMENT ═══
This tool is designed for:
  • Authorized penetration testing (HTB, CTF)
  • Testing your own websites
  • Security research with permission

Do you agree to use Webber ethically? (yes/no): yes

═══ TARGET AUTHORIZATION ═══
Target URL: https://target.htb
Do you have authorization to test this target? (yes/no): yes

[i] Checking robots.txt...
[!] No robots.txt found (proceeding)

═══ READY TO START ═══
Target: https://target.htb
Keywords: 15 loaded
Device Capacity: HIGH
Proxy Pool: 23 proxies

Press ENTER to start Webber...

═══ LIVE STATISTICS ═══
Runtime: 156s
Cycles: 3
Total Visits: 18
Pages Viewed: 87
Time Spent: 45m
Unique Sessions: 18
Natural Behaviors: 23
Bans Avoided: 87
Identity Rotations: 6
IP Rotations: 6
Proxy Pool: 23 active
Avg Pages/Visit: 4.8

✓ Requests appear from different devices & IPs
Press Ctrl+C to stop
```

---

## 🎓 Use Cases

### ✅ Authorized Use
- **HTB/CTF Challenges**: Test traffic handling
- **Own Websites**: Load testing, analytics testing
- **Penetration Testing**: With explicit written permission
- **Security Research**: Educational purposes

### ❌ Prohibited Use
- Attacking websites without authorization
- Fraudulent metric manipulation
- Terms of Service violations
- Malicious activities

---

## ⚙️ How It Works

### Traffic Simulation Flow

```
1. Initialize Session
   ↓
2. Generate Device Fingerprint
   ↓
3. Select Random Proxy (from auto-fetched pool)
   ↓
4. Search Google with Random Keyword (70% of time)
   ↓
5. Visit Target Site
   ↓
6. Read Content (realistic timing)
   ↓
7. Navigate Internal Pages (2-7 pages)
   ↓
8. Simulate Human Behavior (mistakes, distractions)
   ↓
9. Rotate Identity (every 2-3 visits)
   ↓
10. Repeat with Different Device/IP
```

### Identity Rotation

Every 2-3 visits, Webber automatically:
- Switches to random proxy (different IP)
- Generates new device fingerprint
- Changes user agent
- Clears cookies (new session)
- Updates all headers

This makes each visitor appear completely unique.

---

## 🛠️ Troubleshooting

### "Missing dependencies"
**Solution:** Just press **Y** when prompted - auto-installs everything

### "No keywords loaded"
**Solution:** 
```bash
# Create keywords.txt
echo "target keyword" > keywords.txt
echo "another keyword" >> keywords.txt
```

### "Proxy fetch failed"
**Solution:**
- Check internet connection
- Webber will retry automatically
- Or add manual proxies to `proxies.txt`

### "Connection timeout"
**Solution:**
- Normal for free proxies (auto-rotates)
- Consider adding paid proxies to `proxies.txt`

### Slow performance
**Solution:**
- Free proxies can be slow
- Webber auto-detects and skips dead proxies
- Add faster proxies to `proxies.txt` for better speed

---

## 📈 Performance Tips

### 1. Let Auto-Proxy Work
Free proxies are fetched automatically - just let it run!

### 2. Use Quality Keywords
More specific keywords = better targeted traffic simulation

### 3. Optimal Hardware
- **Low RAM (< 4GB)**: 2-4 visits per cycle
- **Medium RAM (4-8GB)**: 3-6 visits per cycle  
- **High RAM (8-16GB)**: 4-8 visits per cycle
- **Ultra RAM (16GB+)**: 5-10 visits per cycle

### 4. Monitor Stats
Watch the live dashboard - if IP rotations stop, proxies may be exhausted

---

## 🔐 Security & Privacy

### What Webber Does
- ✅ Rotates through proxies for IP diversity
- ✅ Spoofs device fingerprints
- ✅ Simulates realistic human behavior
- ✅ Uses random timing patterns

### What Webber Doesn't Do
- ❌ Bypass authentication (not a hacking tool)
- ❌ Exploit vulnerabilities
- ❌ Steal data
- ❌ Perform attacks

**Webber is for authorized traffic simulation only.**

---

## 📚 Advanced Configuration

### Custom Proxy Sources

Edit `webber.py` to add your own proxy APIs:

```python
# Around line 350 in _fetch_free_proxies()
# Add your custom proxy API endpoint
```

### Hardware Override

Force specific capacity:
```python
# Edit detect_hardware_capacity() function
# Change capacity_map values
```

### Behavior Tuning

Adjust randomization in `BehaviorRandomizer` class:
```python
# Reading speeds, attention spans, navigation patterns
```

---

## 🤝 Contributing

Webber is designed for ethical security testing. Contributions welcome:

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

---

## 📜 Legal Disclaimer

**BY USING WEBBER, YOU AGREE:**

1. You have explicit authorization to test the target
2. You will use this tool ethically and legally
3. You accept full responsibility for your actions
4. You will not violate any Terms of Service
5. You will respect rate limits and robots.txt when appropriate

**THE AUTHOR IS NOT RESPONSIBLE FOR MISUSE OF THIS TOOL.**

---

## 📞 Support

### Common Issues
- Check the Troubleshooting section above
- Ensure you have Python 3.7+
- Verify internet connection for proxy fetching

### HTB/CTF Specific
- Use `--robots-mode ignore` for challenges
- Use `--no-consent` to skip prompts
- Let auto-proxy system handle IP rotation

---

## 🎉 Quick Reference

```bash
# Minimal HTB command (auto-everything)
python3 webber.py -t https://target.htb -w keywords.txt --no-consent --robots-mode ignore

# With manual proxies
python3 webber.py -t https://target.htb -w keywords.txt

# Production testing
python3 webber.py -t https://site.com -w keywords.txt --robots-mode respect
```

---

## 📊 Stats Explained

| Stat | Meaning |
|------|---------|
| **Cycles** | Number of complete traffic simulation rounds |
| **Total Visits** | Individual page visits performed |
| **Pages Viewed** | Total pages loaded (including internal navigation) |
| **Time Spent** | Cumulative time spent "reading" content |
| **Unique Sessions** | Different browser sessions created |
| **Identity Rotations** | Times device fingerprint was changed |
| **IP Rotations** | Times proxy was switched |
| **Proxy Pool** | Number of working proxies available |

---

## ⭐ Features at a Glance

| Feature | Status | Description |
|---------|--------|-------------|
| Auto-Install | ✅ | Dependencies install automatically |
| Auto-Proxy | ✅ | Fetches 20+ free proxies |
| Device Spoofing | ✅ | 30+ different devices |
| IP Rotation | ✅ | Automatic proxy switching |
| Human Behavior | ✅ | Realistic browsing patterns |
| Hardware Detection | ✅ | Optimizes for your device |
| Live Dashboard | ✅ | Real-time statistics |
| Cross-Platform | ✅ | Linux, Mac, Windows, Termux |
| Ethical Prompts | ✅ | Forces responsible usage |
| robots.txt Check | ✅ | Respects website preferences |

---

**Made for ethical hackers, by ethical hackers. Happy (legal) testing! 🛡️**

```
    ╦ ╦╔═╗╔╗ ╔╗ ╔═╗╦═╗
    ║║║║╣ ╠╩╗╠╩╗║╣ ╠╦╝
    ╚╩╝╚═╝╚═╝╚═╝╚═╝╩╚═
```
