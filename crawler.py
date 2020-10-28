import sys
import json
from datetime import datetime

import eventlet
import redis

import settings
from models import ProductRecord, Response
from helpers import item_dequeue, item_queue, make_request, log, current_url_listing
from extractors import get_title, get_url, get_price, get_primary_img


crawl_time = datetime.now()

pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)


def begin_crawl():
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines

            response_data = make_request(line)

            saveLoad(response_data, line)


def saveLoad(response_data, line: str):
    response = json.loads(
        response_data['response'].content.decode('utf-8'))

    if response["pc_status"] == 200:
        response["current_listing_url"] = response_data["current_listing_url"]
        item_queue(response)

        currentPage: int = response["body"]["pagination"]["currentPage"]
        totalPages: int = response["body"]["pagination"]["totalPages"]

        if(currentPage != totalPages):
            data = make_request(line)
            # pile.spawn(fetch_items)
            saveLoad(data, line)
        else:
            crawling_elapsed_time = datetime.now() - crawl_time
            log("Finished crawling. Time elapsed {}".format(
                crawling_elapsed_time.seconds))
            return


def fetch_items():

    global crawl_time
    response_string = item_dequeue()
    if not response_string:
        log("WARNING: Error loading response item {0} ".format(
            response_string))
        pile.spawn(item_queue)
        return
    response = json.loads(response_string)

    log("Found {} product items ".format(len(response["body"]["products"])))

    for item in response["body"
                         ]["products"][:settings.max_details_per_listing]:

        product_image = item["image"]
        if not product_image:
            log("No product image detected, skipping")
            continue
        product_title = item["name"]
        product_url = item["url"]
        product_listing_url = response["current_listing_url"]
        product_price = item["price"]
        product_customer_review = item["customerReview"]
        product_customer_review_count = item["customerReviewCount"]
        product_shipping_message = item["shippingMessage"]
        product_is_prime = item["isPrime"]
        product_sponsored_ad = item["sponsoredAd"]
        product_asin = item["asin"]

        product = ProductRecord(
            title=product_title,
            product_url=product_url,
            listing_url=product_listing_url,
            price=product_price,
            primary_img=product_image,
            customer_review=product_customer_review,
            customer_review_count=product_customer_review_count,
            shipping_message=product_shipping_message,
            is_prime=product_is_prime,
            sponsored_ad=product_sponsored_ad,
            asin=product_asin
        )
        product.save()

    # add next page to queue
    # next_link = page.find("a", id="pagnNextLink")
    # if next_link:
    #     log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
    #     enqueue_url(next_link["href"])
    #     pile.spawn(fetch_listing)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        if(sys.argv[1] == "start"):
            r = redis.Redis()
            log("Flushing queue. Current queue count {}".format(
                r.scard("item_queue")))
            r.flushdb()
            log("Flushed queue. Current queue count {}".format(
                r.scard("item_queue")))

            log("Beginning crawl at {}".format(crawl_time))
            begin_crawl()

            [pile.spawn(fetch_items) for _ in range(r.scard("item_queue"))]
            pool.waitall()
