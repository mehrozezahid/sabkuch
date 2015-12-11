import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re

class Khaadi(ClothingBaseSpider):
    name = "khaadi"
    allowed_domains = ["khaadionline.com"]
    start_urls = ["http://www.khaadionline.com/pk/woman.html",
                  "http://www.khaadionline.com/pk/sale.html"]
    brand_id = 11

    rules = (
        Rule(SgmlLinkExtractor(deny=("view-all", "accessories", "unstitched"),
                               restrict_xpaths=(
                                                "//ul[@class='categories-tree']/li[contains(@class,'level1')]/a",
                                                "//*[@title='Next']"
                                                ))),
        # Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@class='pages']//*[contains(@class,'next')]",
        #                                         ))),

        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@class='product-name']/a",
                                                )),
             callback="parse_product"),
    )

    def parse_product(self, response):
        sel = response.xpath("/html")

        item = Garment()
        item['source_url'] = response.url
        item['item_category_name'] = self.get_category(sel)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_secondary_image_urls'] = self.get_secondary_image_urls(response)
        item['item_description'] = self.get_description(sel)
        item['item_price'] = self.get_price(sel)
        item['item_is_available'] = True
        item['item_is_on_sale'] = self.is_on_sale(sel)
        item['item_sale_price'] = self.get_sale_price(sel)
        yield item

    # for item code
    def get_item_code(self, sel):
        return sel.xpath(".//*[@class='product-code']/strong/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath(".//*[@class='std wth-log']//text()").extract()
        return "".join(des)

    # category
    def get_category(self, sel):
        category = sel.xpath(".//*[contains(@class,'breadcrumbs')]//li/a/text()").extract()
        # these categories are demanded in this way by client
        if len(category) > 3:
            return category[2].strip()
        return category[-1].strip() if category else "uncategorized"

    # image url
    def get_image_url(self, response):
        src = response.xpath(".//*[@id='zoom']/@href")
        return response.urljoin(src[0].extract())

    def get_secondary_image_urls(self, response):
        images = response.xpath(".//*[@class='more-views ']//a/@href").extract()
        images.pop(0)
        return images

    # price for product
    def get_price(self, sel):
        price = sel.xpath(".//*[@class='regular-price' or @class='old-price']"
                          "//*[@class='price']/text()").extract()[0].strip()
        return re.sub("PKR ", '', price)

    def is_on_sale(self, sel):
        # on_sale = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()
        on_sale = self.get_category(sel)
        return True if on_sale == "Sale" else False

    def get_sale_price(self, sel):
        if self.get_category(sel) == "Sale":
            sale_price = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()[0].strip()
            return re.sub("PKR ", '', sale_price) if sale_price else None
        return None
