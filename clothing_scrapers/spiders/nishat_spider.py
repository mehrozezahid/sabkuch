from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class NishatSpider(ClothingBaseSpider):
    name = "nishat"
    allowed_domains = ["nishatlinen.com"]
    start_urls = ['http://nishatlinen.com/']
    brand_id = 2

    # first rule is modified as per client's demand using position()
    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@id='header']//ul[contains(@class,'nav')]/li[position()<5]",
                                                "//div[@class='links']//a"
                                                ))),
        Rule(SgmlLinkExtractor(restrict_xpaths=("//div[@class='product']//a",
                                                )),
             callback="parse_product")
    )

    # for each product
    def parse_product(self, response):
        sel = response.xpath("/html")

        item = Garment()
        item['source_url'] = response.url
        item['item_name'] = self.get_item_name(sel)
        item['item_category_name'] = self.get_category(sel, response)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_secondary_image_urls'] = self.get_secondary_image_urls(response)
        item['item_description'] = self.get_description(sel)
        item['item_price'] = self.get_price(sel)
        item['item_is_available'] = True
        item['item_is_on_sale'] = self.is_on_sale(sel, response)
        item['item_sale_price'] = self.get_sale_price(sel, response)
        yield item

    # for item name (if exists)
    def get_item_name(self, sel):
        return None

    # for item code
    def get_item_code(self, sel):
        return sel.xpath(".//*[@id='product']/h1/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath(".//*[@id='tab-description']//p/text()").extract()
        if not des:
            des = sel.xpath(".//*[@id='tab-description']//tr/*/text()").extract()
        return " ".join(des)

    # category
    def get_category(self, sel):
        category = sel.xpath(".//*[@id='product']/ul/li/text()").extract()
        if category:
            return re.sub("Product Code: ", '', category[0].strip())
        return "None"

    # image url
    def get_image_url(self, response):
        src = response.xpath(".//*[@id='zoom1']/@href")
        return response.urljoin(src[0].extract())

    def get_secondary_image_urls(self, response):
        images = response.xpath(".//*[@class='cloud-zoom-gallery item']/@href").extract()
        if len(images) > 1:
            images.pop()
            return images
        return None

    # def get_second_image_url(self, response):
    #     src = response.xpath(".//*[@class='cloud-zoom-gallery item']/@href").extract()
    #     if src:
    #         return response.urljoin(src[0])
    #     return None

    # price for product
    def get_price(self, sel):
        price = sel.xpath("//*[@id='product']//div[@class='price' or [contains(@style,'line-through')]//text()").extract()
        # removing empty results
        price = filter(None, [s.strip() for s in price])
        if price:
            return re.sub("Rs ", '', price[0])
        return "TBA"

    def is_on_sale(self, sel):
        on_sale = sel.xpath("//*[@id='product']//*[@class='special_price']/text()").extract()
        return True if on_sale else False

    def is_available(self, sel):
        # if product coming soon
        if "TBA" in self.get_price(sel):
            return False
        sold = sel.xpath("//*[@id='product']//span[contains(.,'sold')]/text()").extract()
        return False if sold else True

    def get_sale_price(self, sel):
        if self.is_on_sale(sel):
            sale_price = sel.xpath(".//*[@class='special_price']/text()").extract()[0].strip()
            return re.sub("Rs ", '', sale_price) if sale_price else None
        return None
