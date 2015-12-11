import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class SafinazSpider(ClothingBaseSpider):
    name = "sana_safinaz"
    allowed_domains = ["sanasafinaz.com"]
    start_urls = ['http://www.sanasafinaz.com/']
    brand_id = 8

    rules = (
        Rule(SgmlLinkExtractor(deny=("accessories", "Acoustics"),
                               restrict_xpaths=("//*[@class='top-menu']/li/a",
                                                )),
             callback="parse_items"),
    )

    # this will parse all the products on current page
    def parse_items(self, response):
        product_links = response.xpath("//*[@class='product-item']")
        for href in product_links:
            plink = href.xpath(".//*[@class='product-title']/a/@href").extract()
            full_url = response.urljoin(plink[0])
            on_sale = self.is_on_sale(href)
            # manual requests were made because on_sale is not mentioned on item page
            yield scrapy.Request(full_url, callback=self.parse_product, meta={'on_sale': on_sale})

    # for each product
    def parse_product(self, response):
        sel = response.xpath("//*[@class='detail-box']")

        item = Garment()
        item['item_is_on_sale'] = response.meta["on_sale"]
        item['source_url'] = response.url
        item['item_category_name'] = self.get_category(sel)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(sel)
        item['item_image_url'] = self.get_image_url(response)
        item['item_second_image_url'], item['item_third_image_url'] = self.get_secondary_image_urls(response)
        item['item_description'] = self.get_description(sel)
        item['item_is_available'] = True
        item['item_price'] = self.get_price(sel)
        yield item

    # for item code
    def get_item_code(self, sel):
        return sel.xpath(".//*[@itemprop='name']/text()").extract()[0].strip()

    # for product description
    def get_description(self, sel):
        des = sel.xpath(".//*[@class='short-description']/text()").extract()
        return des[0].strip() if des else ""

    # category
    def get_category(self, sel):
        return sel.xpath(".//*[@class='cat-neme']/text()").extract()[0].strip()

    # image url
    def get_image_url(self, response):
        src = response.xpath("//*[@id='zoom1']/@href")
        return response.urljoin(src[0].extract())

    def get_secondary_image_urls(self, response):
        src = response.xpath("//*[@class='cloud-zoom-gallery']/@href").extract()
        if src:
            try:
                if src[1]:
                    try:
                        if src[2]:
                            return response.urljoin(src[1]), response.urljoin(src[2])
                        else:
                            return response.urljoin(src[1]), None
                    except IndexError:
                        return response.urljoin(src[1]), None
                else:
                    return None, None
            except IndexError:
                return None, None
        else:
            return None, None

    # price for product
    def get_price(self, sel):
    	try:
    		price = sel.xpath(".//*[@class='product-price']/span/text()").extract()[0].strip()
        except IndexError:
        	price = sel.xpath(".//*[@class='product-price discounted-price']/span/text()").extract()[0].strip()

        return re.sub("PKR. ", '', price)

    def is_on_sale(self, sel):
        on_sale = sel.xpath(".//*[@class='price old-price']").extract()
        return True if on_sale else False
