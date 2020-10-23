from html.parser import HTMLParser

htmlparser = HTMLParser()


def get_title(item):
    title = item.select("span.a-size-base-plus.a-color-base.a-text-normal")
    if len(title) > 0:
        return title[0].text
    else:
        return "<missing product title>"


def get_url(item):
    link = item.select("a.a-link-normal.a-text-normal")
    if len(link) > 0:
        return link[0]["href"]
    else:
        return "<missing product url>"


def get_price(item):
    symbol = item.find("span", "a-price-symbol")
    value = item.find("span", "a-price-whole")
    fraction = item.find("span", "a-price-fraction")
    fullPrice = "".join([symbol.text if ((symbol is not None) and (len(symbol)) > 0) else "NA", value.text if ((value is not None) and len(
        value) > 0) else "NA", fraction.text if ((fraction is not None) and len(
            value) > 0) else "NA"])
    if fullPrice:
        return fullPrice
    return None


def get_primary_img(item):
    thumb = item.find("img")
    if thumb:
        src = thumb["src"]

        p1 = src.split("/")
        p2 = p1[-1].split(".")

        base = p2[0]
        ext = p2[-1]

        return "/".join(p1[:-1]) + "/" + base + "." + ext

    return None
