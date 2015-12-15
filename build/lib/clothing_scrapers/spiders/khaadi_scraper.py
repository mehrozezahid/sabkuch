import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class KhaadiSpider(ClothingBaseSpider):
    name = "khadi"
    allowed_domains = ["khaadionline.com"]
    # start_urls = ["khaadionline.com/pk"]
    brand_id = 11

    # first rule is modified as per client's demand using position()
    rules = (
        Rule(SgmlLinkExtractor(deny=("view-all", "accessories"),
                               restrict_xpaths=("//*[@id='nav']//li[position() < 4 ]",
                                                "//ul[@class='categories-tree']//li[contains(@class,'level2')]/a",
                                                "//*[@title='Next']"
                                                ))),
        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[contains(@class,'product-grid')]//*[@class='product-image']",
                                                )),
             callback="parse_product")
    )

    def start_requests(self):
        return [scrapy.FormRequest("http://www.khaadionline.com/?",
                                   formdata={'spr': '', 'cddropdown': 'pk', 'submitbutton': 'Enter'}
                                   )]

    # for each product
    def parse_product(self, response):
        sel = response.xpath("/html")

        item = Garment()
        item['source_url'] = response.url
        item['item_category_name'] = self.get_category(sel, response)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_description'] = self.get_description(sel)
        item['item_price'] = self.get_price(sel)
        item['item_is_available'] = True
        item['item_is_on_sale'] = self.is_on_sale(sel)
        yield item

    # for item code
    def get_item_code(self, sel):
        return sel.xpath(".//*[@class='product-code']/strong/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath(".//*[@class='std']//p/text()").extract()
        return " ".join(des)

    # category
    def get_category(self, sel, response):
        category = sel.xpath(".//*[contains(@class,'breadcrumbs')]//li/a/text()").extract()
        # these categories are demanded in this way by client
        if len(category) > 3:
            referrer_url = response.request.headers.get('Referer', None)
            if "sale" in referrer_url:
                return category[1].strip()
            return category[2].strip()
        return category[-1].strip() if category else "uncategorized"

    # image url
    def get_image_url(self, response):
        src = response.xpath(".//*[@id='zoom']/@href")
        return response.urljoin(src[0].extract())

    # price for product
    def get_price(self, sel):
        price = sel.xpath(".//*[@class='regular-price' or @class='special-price']"
                          "//*[@class='price']/text()").extract()[0].strip()
        return re.sub("PKR ", '', price)

    def is_on_sale(self, sel):
        on_sale = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()
        return True if on_sale else False
