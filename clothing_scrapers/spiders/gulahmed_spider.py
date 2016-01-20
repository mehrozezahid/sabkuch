import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class GulAhmedSpider(ClothingBaseSpider):
    name = "gul_ahmed"
    allowed_domains = ["gulahmedshop.com"]
    start_urls = ['https://www.gulahmedshop.com/']
    brand_id = 3

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=("//*[@id='site-menu']//ul[contains(@class,'mega-sub')]",))),
        Rule(SgmlLinkExtractor(deny=("PriceCondition",), restrict_xpaths=("//*[@id='brands-list']",
                                                                          "//a[@data-title='Next Page']")),
             follow=True,
             callback="parse_items")
    )

    # this will parse all the products on current page
    def parse_items(self, response):
        # getting all products on current page
        product_links = response.xpath("//*[@id='main-content']//div[@class='product']")
        for href in product_links:
            plink = href.xpath(".//div[@class='entry-media']/a/@href").extract()
            full_url = response.urljoin(plink[0])
            # availability of item
            availability = self.get_availability(href)
            yield scrapy.Request(full_url, callback=self.parse_product, meta={'availability': availability})

    # for each product
    def parse_product(self, response):
        sel = response.xpath("/html")

        item = Garment()
        item['item_is_available'] = response.meta["availability"]
        item['source_url'] = response.url
        item['item_category_name'] = self.get_category(sel)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_description'] = self.get_description(sel)
        item['item_price'] = self.get_price(sel)
        yield item

    # for item code
    def get_item_code(self, sel):
        return sel.xpath("//*[@id='main-content']//header//h3/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath("//*[@id='product-description']//p//text()").extract()
        return des[0] if des else ""

    # category
    def get_category(self, sel):
        return sel.xpath("//*[@id='main-content']//header//h2/text()").extract()[0].strip()

    # image url
    def get_image_url(self, response):
        src = response.xpath("//img[@id='zoom1']/@src")
        return response.urljoin(src[0].extract())

    # price for product
    def get_price(self, sel):
        price = sel.xpath("//article[@class='entry-content']"
                          "//span[contains(.,'Price')]/following::span[1]//text()").extract()[0].strip()
        return re.sub("Rs. ", '', price)

    def get_availability(self, sel):
        available = sel.xpath(".//div[@class='entry-main']//span/text()").extract()[0]
        return not "Not" in available
