"""
Website Engagement Bot API
Simulates realistic user behavior to improve engagement metrics for any website
"""

import sys
import time
import os
import json
from urllib.parse import quote_plus, urljoin, urlparse
import re
import threading
from datetime import datetime
import random

try:
    import requests
    from bs4 import BeautifulSoup
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    DEPENDENCIES_OK = True
except ImportError:
    DEPENDENCIES_OK = False
    print("Missing dependencies! Install: pip install requests beautifulsoup4 flask flask-cors")

# Check if running in Termux
IS_TERMUX = os.path.exists('/data/data/com.termux')

# Global variables for bot control
bot_status = {
    'running': False,
    'run_count': 0,
    'last_run_time': None,
    'current_phase': 'Idle',
    'total_pages_visited': 0,
    'total_time_spent': 0,
    'engagement_score': 0,
    'results': [],
    'latest_summary': {}
}
bot_thread = None
stop_bot_flag = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class EngagementBot:
    def __init__(self, mobile=True):
        """Initialize the bot with realistic browser behavior"""
        self.session = requests.Session()
        
        # Rotate between different realistic user agents
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
        ]
        
        self.update_headers()
    
    def update_headers(self):
        """Update headers with random user agent"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',  # Simulate coming from Google
        }
        self.session.headers.update(headers)
    
    def search_and_click(self, query, target_url="https://nmhss.onrender.com"):
        """
        Search Google for query and 'click' on target_url if found
        This simulates organic traffic from search engines
        Replace target_url with your own website URL
        """
        try:
            # Perform Google search
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            # Random delay before search (1-3 seconds)
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all search result links
                links = soup.find_all('a', href=True)
                found_target = False
                
                for link in links:
                    href = link.get('href', '')
                    if target_url in href:
                        found_target = True
                        break
                
                # Simulate reading search results (2-5 seconds)
                time.sleep(random.uniform(2, 5))
                
                return found_target
            
            return False
                
        except Exception as e:
            return False
    
    def visit_page_naturally(self, url):
        """
        Visit a page and simulate natural human behavior:
        - Scroll through content
        - Read text (stay for realistic time)
        - Click on internal links
        - Interact with elements
        Works with any website - just provide the URL
        """
        page_data = {
            'url': url,
            'visit_duration': 0,
            'pages_visited': 0,
            'links_clicked': [],
            'forms_interacted': 0
        }
        
        try:
            # Update referer to simulate coming from Google
            self.session.headers['Referer'] = f'https://www.google.com/search?q={urlparse(url).netloc.replace(".", "+")}'
            
            # Visit main page
            start_time = time.time()
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Simulate reading the page content
                # Calculate realistic read time based on content
                text_content = soup.get_text()
                word_count = len(text_content.split())
                # Average reading speed: 200-250 words per minute
                read_time = (word_count / 225) * 60  # seconds
                # Add some randomness (people read at different speeds)
                read_time = random.uniform(read_time * 0.7, read_time * 1.3)
                # Cap between 30 seconds and 5 minutes
                read_time = max(30, min(300, read_time))
                
                bot_status['current_phase'] = f'Reading page content ({int(read_time)}s)'
                
                # Simulate scrolling by breaking read time into chunks
                scroll_intervals = int(read_time / 5)
                for i in range(scroll_intervals):
                    if stop_bot_flag:
                        break
                    time.sleep(5)
                    # Simulate scroll by making small requests
                
                page_data['pages_visited'] += 1
                
                # Find and click internal links (simulate exploring the site)
                internal_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    # Only internal links
                    if href and (href.startswith('/') or url in href) and '#' not in href:
                        full_url = urljoin(url, href)
                        if full_url not in internal_links and full_url != url:
                            internal_links.append(full_url)
                
                # Visit 2-4 random internal pages
                pages_to_visit = min(len(internal_links), random.randint(2, 4))
                
                for i in range(pages_to_visit):
                    if stop_bot_flag:
                        break
                    
                    if i < len(internal_links):
                        next_page = internal_links[i]
                        bot_status['current_phase'] = f'Visiting internal page {i+1}/{pages_to_visit}'
                        
                        # Update referer to previous page
                        self.session.headers['Referer'] = url
                        
                        # Random delay before clicking link (2-8 seconds)
                        time.sleep(random.uniform(2, 8))
                        
                        try:
                            page_response = self.session.get(next_page, timeout=15)
                            if page_response.status_code == 200:
                                page_data['links_clicked'].append(next_page)
                                page_data['pages_visited'] += 1
                                
                                # Read this page too (shorter time)
                                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                                page_text = page_soup.get_text()
                                page_words = len(page_text.split())
                                page_read_time = max(15, min(90, (page_words / 225) * 60))
                                
                                time.sleep(random.uniform(page_read_time * 0.5, page_read_time))
                                
                        except:
                            pass
                
                # Check for forms and simulate interaction
                forms = soup.find_all('form')
                if forms and random.random() > 0.5:  # 50% chance to interact with forms
                    bot_status['current_phase'] = 'Interacting with form'
                    time.sleep(random.uniform(3, 8))  # Time to fill form
                    page_data['forms_interacted'] += 1
                
                # Calculate total time spent
                page_data['visit_duration'] = time.time() - start_time
                
        except Exception as e:
            page_data['error'] = str(e)
        
        return page_data
    
    def simulate_multiple_visits(self, url, num_visits=5):
        """
        Simulate multiple user visits with different patterns
        Customize the keywords list below with your own website keywords
        """
        all_visits = []
        
        # CUSTOMIZE: Replace these with your own website keywords
        keywords = [
            "nmhss thirunavaya",
            "navamukunda higher secondary school",
            "nmhss school code",
            "navamukunda hss thirunavaya",
            "nmhss admin portal",
        ]
        
        for visit_num in range(num_visits):
            if stop_bot_flag:
                break
            
            bot_status['current_phase'] = f'Simulating visit {visit_num + 1}/{num_visits}'
            
            # Randomly choose whether to come from search or direct
            from_search = random.random() > 0.3  # 70% from search, 30% direct
            
            if from_search:
                # Search for random keyword
                keyword = random.choice(keywords)
                bot_status['current_phase'] = f'Searching: {keyword}'
                self.search_and_click(keyword, url)
            
            # Update user agent for variety
            self.update_headers()
            
            # Visit the site naturally
            visit_data = self.visit_page_naturally(url)
            all_visits.append(visit_data)
            
            bot_status['total_pages_visited'] += visit_data['pages_visited']
            bot_status['total_time_spent'] += visit_data['visit_duration']
            
            # Random delay between visits (simulate different users)
            delay = random.uniform(30, 120)  # 30 seconds to 2 minutes
            bot_status['current_phase'] = f'Waiting between visits ({int(delay)}s)'
            
            for _ in range(int(delay)):
                if stop_bot_flag:
                    break
                time.sleep(1)
        
        return all_visits


def run_bot_loop():
    """
    Run the bot in a continuous loop with realistic engagement
    CUSTOMIZE: Change target_url to your own website
    """
    global bot_status, stop_bot_flag
    
    bot = EngagementBot(mobile=True)
    
    # CUSTOMIZE: Replace with your website URL
    target_url = "https://nmhss.onrender.com"
    
    while not stop_bot_flag:
        try:
            bot_status['run_count'] += 1
            bot_status['last_run_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Simulate 3-5 realistic user visits per run
            num_visits = random.randint(3, 5)
            bot_status['current_phase'] = f'Starting {num_visits} user simulations'
            
            visits = bot.simulate_multiple_visits(target_url, num_visits)
            
            if stop_bot_flag:
                break
            
            # Calculate engagement score
            avg_time = bot_status['total_time_spent'] / max(bot_status['run_count'], 1)
            avg_pages = bot_status['total_pages_visited'] / max(bot_status['run_count'], 1)
            engagement_score = min(100, int((avg_time / 60) * 10 + avg_pages * 5))
            bot_status['engagement_score'] = engagement_score
            
            # Update results
            result_entry = {
                'run_number': bot_status['run_count'],
                'timestamp': bot_status['last_run_time'],
                'visits_simulated': num_visits,
                'total_pages_visited': bot_status['total_pages_visited'],
                'total_time_spent_minutes': round(bot_status['total_time_spent'] / 60, 2),
                'engagement_score': engagement_score,
                'visit_details': visits[-3:]  # Keep last 3 visits
            }
            
            bot_status['results'].append(result_entry)
            bot_status['latest_summary'] = result_entry
            
            # Keep only last 10 results to save memory
            if len(bot_status['results']) > 10:
                bot_status['results'] = bot_status['results'][-10:]
            
            bot_status['current_phase'] = 'Waiting for next cycle'
            
            # Wait 10-15 minutes between cycles (realistic user pattern)
            wait_time = random.randint(600, 900)  # 10-15 minutes
            for _ in range(wait_time):
                if stop_bot_flag:
                    break
                time.sleep(1)
            
        except Exception as e:
            bot_status['current_phase'] = f'Error: {str(e)}'
            time.sleep(30)
    
    bot_status['running'] = False
    bot_status['current_phase'] = 'Stopped'


# API Endpoints

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current bot status"""
    return jsonify(bot_status)

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the engagement bot"""
    global bot_thread, stop_bot_flag, bot_status
    
    if bot_status['running']:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    stop_bot_flag = False
    bot_status['running'] = True
    bot_status['current_phase'] = 'Starting...'
    
    bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
    bot_thread.start()
    
    return jsonify({'success': True, 'message': 'Engagement bot started - simulating realistic user behavior'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    global stop_bot_flag, bot_status
    
    if not bot_status['running']:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    stop_bot_flag = True
    bot_status['current_phase'] = 'Stopping...'
    
    return jsonify({'success': True, 'message': 'Bot stop signal sent'})

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get all results"""
    return jsonify({'results': bot_status['results']})

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get latest summary"""
    return jsonify(bot_status['latest_summary'])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    stats = {
        'total_runs': bot_status['run_count'],
        'total_pages_visited': bot_status['total_pages_visited'],
        'total_time_spent_hours': round(bot_status['total_time_spent'] / 3600, 2),
        'engagement_score': bot_status['engagement_score'],
        'average_time_per_visit': round(bot_status['total_time_spent'] / max(bot_status['total_pages_visited'], 1), 2),
        'is_running': bot_status['running']
    }
    return jsonify(stats)

@app.route('/', methods=['GET'])
def home():
    """API documentation - Works with any website"""
    docs = {
        'name': 'Website Engagement Bot API',
        'version': '2.0',
        'description': 'Simulates realistic user engagement to improve site metrics for any website',
        'setup': {
            'step_1': 'Edit run_bot_loop() function - change target_url to your website',
            'step_2': 'Edit simulate_multiple_visits() - add your keywords',
            'step_3': 'Deploy and start the bot via /api/start'
        },
        'endpoints': {
            '/api/status': 'GET - Get current bot status',
            '/api/start': 'POST - Start the engagement bot',
            '/api/stop': 'POST - Stop the bot',
            '/api/results': 'GET - Get all results (last 10 runs)',
            '/api/summary': 'GET - Get latest run summary',
            '/api/stats': 'GET - Get overall engagement statistics'
        },
        'features': {
            'realistic_behavior': 'Simulates human reading patterns and navigation',
            'search_traffic': 'Comes from Google searches (70% of visits)',
            'internal_navigation': 'Clicks 2-4 internal links per visit',
            'time_on_site': '30s - 5min per page based on content length',
            'multiple_visits': '3-5 users per cycle',
            'varied_user_agents': 'Different devices and browsers'
        },
        'metrics_improved': [
            'Time on site',
            'Pages per session',
            'Bounce rate',
            'Internal link clicks',
            'Organic search traffic signals'
        ]
    }
    return jsonify(docs)


if __name__ == "__main__":
    if not DEPENDENCIES_OK:
        print("❌ Missing dependencies!")
        print("Install: pip install requests beautifulsoup4 flask flask-cors")
        sys.exit(1)
    
    print("="*60)
    print("🚀 Website Engagement Bot API Server")
    print("="*60)
    print("\n📊 Improves User Engagement Metrics for Any Website:")
    print("  ✓ Time on site")
    print("  ✓ Pages per session")
    print("  ✓ Bounce rate reduction")
    print("  ✓ Internal navigation")
    print("  ✓ Organic traffic signals")
    print("\n⚙️  SETUP: Edit the code to customize:")
    print("  1. Change target_url in run_bot_loop()")
    print("  2. Update keywords in simulate_multiple_visits()")
    print("\n🌐 API Endpoints:")
    print("  GET  /api/status   - Get bot status")
    print("  POST /api/start    - Start engagement bot")
    print("  POST /api/stop     - Stop the bot")
    print("  GET  /api/stats    - Get engagement statistics")
    print("\n🚀 Starting server...")
    
    # Get port from environment variable (for Render.com or any hosting)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"   Server running on port: {port}")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
