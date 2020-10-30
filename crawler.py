import sys
import json
import time
from datetime import datetime

import eventlet
import redis

import settings
from models import ProductRecord, Response
from helpers import item_dequeue, item_queue, make_request, log, browser_request
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from lxml import html
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

        product_asin = item["asin"]

        if not product_asin:
            log("No asin detected, skipping")
            continue
        product_image = item["image"]
        # getProductComments(item["url"],product_asin)
        product_title = item["name"]
        product_url = item["url"]
        product_listing_url = response["current_listing_url"]
        product_price = item["price"]
        product_customer_review = item["customerReview"]
        product_customer_review_count = item["customerReviewCount"]
        product_shipping_message = item["shippingMessage"]
        product_is_prime = item["isPrime"]
        product_sponsored_ad = item["sponsoredAd"]

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


def getProductComments(product_url: str, product_asin: str):

    url_paths = PurePosixPath(
        unquote(
            urlparse(
                product_url
            ).path
        )
    ).parts

    product_name_path = url_paths[1]
    product_asin_path = url_paths[3]

    product_comments_url = "https://www.amazon.co.uk/{0}/product-reviews/{1}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews".format(
        product_name_path, product_asin_path)

    if product_asin_path != product_asin:
        raise Exception("Product asin mismatch! url :{0} product: {1}".format(
            product_asin_path, product_asin))

    all_comments_page = browser_request(product_comments_url)

    all_comments_list = html.fromstring(
        all_comments_page.decode()).xpath("//*[@id='cm_cr-review_list']")

    reviews = []

    for review_index in range(len(all_comments_list[0])):
        review = {}
        review_id: str = ""
        if("id" in all_comments_list[0][review_index].attrib):
            review_id = all_comments_list[0][review_index].attrib["id"]
            review['id'] = review_id
            if(review_id):
                review_rating_div = all_comments_list[0][review_index].xpath(
                    "//*[@id='customer_review-{0}']/div[2]/a[1]".format(review_id))
                if len(review_rating_div):
                    review_rating = review_rating_div[0].attrib["title"]
                    review["rating"] = review_rating
            else:
                review_rating_div = all_comments_list[0][review_index].xpath(
                    "//*[@id='customer_review_foreign-{0}']/div[2]/i/span/text()".format(review_id))
                if len(review_rating_div):
                    review_rating = review_rating_div[0]
                    review["rating"] = review_rating

            review_description_div = all_comments_list[0][review_index].xpath(
                "//*[@id='customer_review-{0}']/div[2]/a[2]/span/text()".format(review_id))

            if(len(review_description_div)):
                review_description = review_description_div[0]
                review["description"] = review_description

            else:
                review_description_div = all_comments_list[0][review_index].xpath(
                    "//*[@id='customer_review_foreign-{0}']/div[2]/span[2]/span".format(review_id))

                if(len(review_description_div)):
                    review_description = review_description_div[0]
                    review["description"] = review_description.text

            review_date_div = all_comments_list[0][review_index].xpath(
                "//*[@id='customer_review-{0}']/span".format(review_id))

            if(len(review_date_div)):
                review_date = review_date_div[0].text
                review["date"] = review_date
            else:
                review_date_div = all_comments_list[0][review_index].xpath(
                    "//*[@id='customer_review_foreign-{0}']/span".format(review_id))
                if(len(review_date_div)):
                    review_date = review_date_div[0].text
                    review["date"] = review_date

            review_item_description_div = all_comments_list[0][review_index].xpath(
                "//*[@id='customer_review-{0}']/div[3]/a".format(review_id))

            if(len(review_item_description_div)):
                review_item_description = review_item_description_div[0].text
                review["item_description"] = review_item_description
            else:
                review_item_description_div = all_comments_list[0][review_index].xpath(
                    "//*[@id='customer_review_foreign-{0}']/div[3]/a/text()".format(review_id))

                if(len(review_item_description_div)):
                    review_item_description = ",".join(
                        review_item_description_div)
                    review["item_description"] = review_item_description

            review_text_div = all_comments_list[0][review_index].xpath(
                "//*[@id='customer_review-{0}']/div[4]/span/span/text()".format(review_id))

            if len(review_text_div):
                review_text = review_text_div[0]
                review["text"] = review_text
            else:
                review_text_div = all_comments_list[0][review_index].xpath(
                    "//*[@id='customer_review_foreign-{0}']/div[4]/span/span/text()".format(review_id))
                if len(review_text_div):
                    review_text = review_text_div[0]
                    review["text"] = review_text

            reviews.append(review)

    return reviews


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
    if(sys.argv[1] == "test"):
        customer_review_page = getProductComments(
            'https://www.amazon.co.uk/State-Cashmere-Pullover-Hoodie-Drawstring/product-reviews/B07MZ3HCXJ/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews', "B07MZ3HCXJ")
