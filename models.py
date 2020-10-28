from eventlet.patcher import original
import psycopg2
from typing import List

import settings
conn = psycopg2.connect(database=settings.database, host=settings.host,
                        port=settings.port, user=settings.user, password=settings.password)
cur = conn.cursor()


class ProductRecord(object):
    """docstring for ProductRecord"""

    def __init__(self, title: str = "", product_url: str = "", listing_url: str = "", price: int = None, primary_img: str = "", customer_review: str = "", customer_review_count: int = None, shipping_message: str = "", is_prime: bool = None, sponsored_ad: bool = None, asin: str = None):
        self.title = title
        self.product_url = product_url
        self.listing_url = listing_url
        self.price = price
        self.primary_img = primary_img
        self.customer_review = customer_review
        self.customer_review_count = customer_review_count
        self.shipping_message = shipping_message
        self.is_prime = is_prime
        self.sponsored_ad = sponsored_ad
        self.asin = asin
        return

    def save(self):
        cur.execute("INSERT INTO products (title, product_url, listing_url, price, primary_img, customer_review,customer_review_count,shipping_message,is_prime,sponsored_ad,asin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", (
            self.title,
            self.product_url,
            self.listing_url,
            self.price,
            self.primary_img,
            self.customer_review,
            self.customer_review_count,
            self.shipping_message,
            self.is_prime,
            self.sponsored_ad,
            self.asin
        ))
        conn.commit()
        return cur.fetchone()[0]


class Pagination(object):
    """docstring for Pagination"""

    def __init__(self, currentPage: int = None, nextPage: int = None, totalPages: int = None):
        self.currentPage = currentPage
        self.nextPage = nextPage
        self.totalPages = totalPages
        return


class Body(object):
    """docstring for Body"""

    def __init__(self, resultInfo: str = "", pagination: Pagination = None, products: List[ProductRecord] = None):
        self.products = [] if products is None else products
        self.resultInfo = resultInfo
        self.pagination = pagination
        return


class Response(object):
    """docstring for Response"""

    def __init__(self, remaining_requests: int = None, original_status: int = None, pc_status: str = None, url: str = None, body: Body = None):
        self.remaining_requests = remaining_requests,
        self.original_status = original_status,
        self.pc_status = pc_status,
        self.url = url,
        self.body = body
        return


if __name__ == '__main__':

    # setup tables
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("""CREATE TABLE products (
        id          serial PRIMARY KEY,
        title       varchar(2056),
        product_url         varchar(2056),
        listing_url varchar(2056),
        price       varchar(128),
        primary_img varchar(2056),
        customer_review varchar(2056),
        customer_review_count varchar (256),
        shipping_message varchar(2056),
        is_prime boolean,
        sponsored_ad boolean,
        asin varchar(256)
    );""")
    conn.commit()
