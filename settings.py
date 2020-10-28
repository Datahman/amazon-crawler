import os
from fake_useragent import UserAgent

current_dir = os.path.dirname(os.path.realpath(__file__))

# Database
database = "postgres"
host = "localhost"
user = "postgres"
port = 5432
password = "postgres"

# Redis
redis_host = "localhost"
redis_port = 6379
redis_db = 0

# Request
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
}

# ua = UserAgent()
# headers = {'User-Agent': ua.random,
#            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#            'Accept-Encoding': 'none',
#            'Accept-Language': 'en-US,en;q=0.8',
#            'Connection': 'keep-alive'}

allowed_params = ["node", "rh", "page"]

# Proxies
proxies = [
    # your list of proxy IP addresses goes here
    # check out https://proxybonanza.com/?aff_id=629
    # for a quick, easy-to-use proxy service
]
proxy_user = ""
proxy_pass = ""
proxy_port = ""

# Crawling Logic
start_file = os.path.join(current_dir, "start-urls.txt")
max_requests = 2 * 10**6  # two million
max_details_per_listing = 9999

# Threads
max_threads = 200

# Logging & Storage
log_stdout = True
image_dir = "/tmp/crawl_images"
export_dir = "/tmp"
