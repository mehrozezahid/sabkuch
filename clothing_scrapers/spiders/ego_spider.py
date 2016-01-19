import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class Ego(ClothingBaseSpider):
    name = "ego"
    allowed_domains = ["wearego.com"]
    start_urls = ["http://www.wearego.com"]
    brand_id = 10

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=(
            "//*[@class='category_name'][not(contains(text(), 'Accessories'))]/parent::a",
                                                ))),
        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@title='Next']",
                                                ))),
        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@class='category-products']//*[@class='product-name']/a",
                                                )),
             callback="parse_product"),
    )

    def parse_product(self, response):
        sel = response.xpath("/html")

        item = Garment()
        item['source_url'] = response.url
        item['item_name'] = self.get_item_name(sel)
        item['item_category_name'] = self.get_category(response)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_secondary_image_urls'] = self.get_secondary_image_urls(response)
        item['item_description'] = self.get_description(sel)
        item['item_price'] = self.get_price(sel)
        item['item_is_available'] = self.is_available(sel)
        item['item_is_on_sale'] = self.is_on_sale(sel, response)
        item['item_sale_price'] = self.get_sale_price(sel, response)
        yield item

    # for item name (if exists)
    def get_item_name(self, sel):
        item_name = sel.xpath(".//*[@class='product-name']/h1/text()").extract()[0]
        return item_name if item_name else None

    # for item code
    def get_item_code(self, sel):
        return sel.xpath(".//*[@class='product-code']/span/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath(".//*[@class='std']//text()").extract()[0]
        return des
        # return "".join(des)

    # category
    def get_category(self, response):
        category = response.xpath(".//*[contains(@class,'breadcrumbs')]//li")
        if len(category) > 2:
            category = category.xpath("//li[position()=2]/a/text()").extract()[0]
        else:
            referrer_url = response.request.headers.get('Referer', None)
            category = referrer_url.split('/')
            if "accessories" in referrer_url:
                return category[2]
            return category[1]
        return category

    # image url
    def get_image_url(self, response):
        src = response.xpath(".//*[@id='image-zoom']/@href")
        return response.urljoin(src[0].extract())

    def get_secondary_image_urls(self, response):
        images = response.xpath("//*[contains(@class, 'cloud-zoom-gallery')]/@href").extract()
        images = self.uniquify_list(images)
        images.pop(0)
        return images

    # price for product
    def get_price(self, sel):
        price = sel.xpath(".//*[@class='regular-price' or @class='old-price']"
                          "//*[@class='price']/text()").extract()[0].strip()
        return re.sub("PKR ", '', price)

    def is_on_sale(self, sel, response):
        on_sale = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()
        return True if on_sale else False

    def is_available(self, sel):
        is_available = sel.xpath("//*[contains(text(),'Out of stock')]")
        return True if is_available else False

    def get_sale_price(self, sel, response):
        sale_price = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()[0].strip()
        return re.sub("PKR ", '', sale_price) if sale_price else None
        return None

    # takes list and removes duplicates
    def uniquify_list(self, seq, idfun=None):
        # order preserving
        if idfun is None:
            def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            # in old Python versions:
            # if seen.has_key(marker)
            # but in new ones:
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result
