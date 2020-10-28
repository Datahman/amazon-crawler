from models import ProductRecord, Response
import settings
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import redis
import os
import random
import json
from datetime import datetime
from urllib.parse import urlparse
from urllib.parse import quote, unquote

import eventlet
requests = eventlet.import_patched('requests.__init__')
time = eventlet.import_patched('time')


num_requests = 0
current_url_listing: str = ""
currentKey: int = 0

redis = redis.StrictRedis(host=settings.redis_host,
                          port=settings.redis_port, db=settings.redis_db)


def make_request(url, return_soup=True):

    global num_requests
    if num_requests >= settings.max_requests:
        raise Exception("Reached the max number of requests: {}".format(
            settings.max_requests))

    proxies = get_proxy()
    try:
        num_requests += 1
        proxyURL = "https://api.proxycrawl.com/scraper?token=kdopUpW3iBdlvQkyy0hbyA&url="

        paginated_url = "{0}&page={1}".format(
            url, num_requests)
        paginated_url = quote(paginated_url)

        encodedURL = proxyURL+paginated_url

        log("Making Request on paginated URL {0} ".format(
            unquote(paginated_url)))
        r = requests.get(
            encodedURL, headers=settings.headers, proxies=proxies)
    except RequestException as e:
        log("WARNING: Request for {} failed, trying again.".format(url))
        return make_request(url)  # try request again, recursively

    if r.status_code != 200:
        os.system('say "Got non-200 Response"')
        log("WARNING: Got a {} status code for URL: {}".format(r.status_code, url))
        return None

    if return_soup:
        response_dict = {}
        response_dict['response'] = r
        response_dict['current_listing_url'] = unquote(paginated_url)
        return response_dict
    return r


# def format_url(url):
    # make sure URLs aren't relative, and strip unnecssary query args
    u = urlparse(url)

    scheme = u.scheme or "https"
    host = u.netloc or "www.amazon.com"
    path = u.path

    if not u.query:
        query = ""
    else:
        query = "?"
        if(type(u.query) is str):
            for piece in u.query.split("&"):
                if "=" in piece:
                    k, v = piece.split("=")
                    if k in settings.allowed_params:
                        query += "{k}={v}&".format(**locals())
            query = query[:-1]

    return "{scheme}://{host}{path}{query}".format(**locals())


def log(msg):
    # global logging function
    if settings.log_stdout:
        try:
            print("{}: {}".format(datetime.now(), msg))
        except UnicodeEncodeError:
            pass  # squash logging errors in case of non-ascii text


def get_proxy():
    # choose a proxy server to use for this request, if we need one
    if not settings.proxies or len(settings.proxies) == 0:
        return None

    proxy_ip = random.choice(settings.proxies)
    proxy_url = "socks5://{user}:{passwd}@{ip}:{port}/".format(
        user=settings.proxy_user,
        passwd=settings.proxy_pass,
        ip=proxy_ip,
        port=settings.proxy_port,

    )
    return {
        "http": proxy_url,
        "https": proxy_url
    }


def item_queue(item: dict):
    itemJson: str = json.dumps(item, indent=4)
    return redis.sadd("item_queue", itemJson)


def item_dequeue():
    return redis.spop("item_queue")


if __name__ == '__main__':
    # test proxy server IP masking
    r = make_request('https://api.ipify.org?format=json', return_soup=False)
    print(r.text)
