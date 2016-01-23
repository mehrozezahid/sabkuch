from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class AlkaramSpider(ClothingBaseSpider):
    name = "alkaram"
    allowed_domains = ["alkaramstudio.com"]
    start_urls = ['http://www.alkaramstudio.com/pk']
    brand_id = 12

    rules = (
        Rule(SgmlLinkExtractor(allow=("women", "sale"),
                               restrict_xpaths=("//*[@class='level-top']",
                                                ))),
        Rule(SgmlLinkExtractor(restrict_xpaths=("//a[contains(., 'View All')]",
                                                "//a[@title='Next']"
                                                ))),
        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@class='product-name']",
                                                )),
             callback="parse_product")
    )

    # for each product
    def parse_product(self, response):
        sel = response.xpath("//*[@class='product-essential']")

        item = Garment()

        item['item_is_available'] = True
        item['source_url'] = response.url
        item['item_name'] = self.get_item_name(sel)
        item['item_category_name'] = self.get_category(sel)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_secondary_image_urls'] = self.get_secondary_image_urls(response)
        item['item_description'] = self.get_description(sel)
        item['item_price'] = self.get_price(sel)
        item['item_is_on_sale'] = self.is_on_sale(sel)
        item['item_sale_price'] = self.get_sale_price(sel)
        yield item

    # for item name (if exists)
    def get_item_name(self, sel):
       item_name = sel.xpath("//*[@class='product-essential']//*[@class='product-name']//text()").extract()
       item_name = filter(None, [s.strip() for s in item_name])
       return item_name if item_name else None

    # for item code
    def get_item_code(self, sel):
        return sel.xpath(".//*[@class='product-name']/h1/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath(".//tbody/tr[contains(.,'Description')]//td//text()").extract()
        return " ".join(des)

    # category
    def get_category(self, sel):
        category = sel.xpath(".//tr[contains(.,'Category')]//td/text()").extract()
        if not category:
            category = sel.xpath(".//tr[contains(.,'Design')]//td/text()")
        return category[0].strip() if category else None

    # image url
    def get_image_url(self, response):
        src = response.xpath(".//*[@id='image-zoom']/@href")
        return response.urljoin(src[0].extract())

    # urls of all other images
    def get_secondary_image_urls(self, response):
        src = response.xpath("//*[contains(@class, 'cloud-zoom-gallery')]/@href").extract()
        if src:
            try:
                return src[1:3]
            except IndexError:
                return src[1] if src[1] else None
        else:
            return None

    # price for product
    def get_price(self, sel):
        price = sel.xpath(".//*[@class='regular-price' or @class='old-price']"
                          "//*[@class='price']/text()").extract()[0].strip()
        return re.sub("PKR ", '', price)

    def is_on_sale(self, sel):
        on_sale = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()
        return True if on_sale else False

    def get_sale_price(self, sel):
        try:
            sale_price = sel.xpath(".//*[@class='special-price']//*[@class='price']/text()").extract()[0].strip()
        except IndexError:
            return None
        return re.sub("PKR ", '', sale_price)
