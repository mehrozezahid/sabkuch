# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from clothing_scrapers.items import Garment
from clothing_scrapers.spiders.ClothingBaseSpider import ClothingBaseSpider
import re


class MariaB_spider(ClothingBaseSpider):
    name = "mariab"
    allowed_domains = ["mariab.pk"]
    start_urls = ['http://www.mariab.pk/']
    brand_id = 13
    rules = (Rule(SgmlLinkExtractor(restrict_xpaths=(
        "//*[@class='queldorei']//li", "//*[@class='toolbar-dropdown over']//li[4]"))),
             Rule(SgmlLinkExtractor(allow=(".html",), restrict_xpaths=("//*[@class='regular']",)),
                  callback="parse_product"))

    # for each product
    def parse_product(self, response):
        item = Garment()
        item['item_is_available'] = self.check_availability(response)
        item['source_url'] = response.url
        item['item_name'] = self.get_item_name(response)
        item['item_category_name'] = self.get_category(response)
        item['item_brand_id'] = self.brand_id
        item['item_code'] = self.get_item_code(response)
        item['item_image_url'] = self.get_image_url(response)
        item['item_secondary_image_urls'] = self.get_secondary_image_urls(response)
        item['item_description'] = self.get_description(response)
        item['item_price'] = self.get_price(response)
        item['item_is_on_sale'] = self.is_on_sale(response)
        item['item_sale_price'] = self.get_sale_price(response)
        yield item

    # for item name (if exists)
    def get_item_name(self, sel):
        return sel.xpath("//*[@class= 'product-name']/h1/text()").extract()

    # for item code
    def get_item_code(self, sel):
        return sel.xpath("//*[@class='sku']/span/text()").extract()

    # for product description
    def get_description(self, sel):
        return sel.xpath("//*[@id='accordion']/div/text()").extract()[0].strip()

    # category
    def get_category(self, sel):
        return sel.xpath("//*[@class='breadcrumbs']//li/a//text()").extract()[-1]

    # image url
    def get_image_url(self, response):
        return response.xpath("//*[@class='product-image']/a/@href").extract()

    # urls of all other images
    def get_secondary_image_urls(self, response):
        return response.xpath("//*[@class='cloud-zoom-gallery']/@href").extract()[1:]

    # price for product
    def get_price(self, sel):
        price = sel.xpath("//*[@class='regular-price' or @class='old-price']//text()").extract()
        print price
        return re.sub("PKR", '', price[-2])

    def is_on_sale(self, sel):
        on_sale = sel.xpath(
                "//*[@class='product-shop-info']//*[@class='special-price']//*[@class='price']/text()").extract()
        return True if on_sale else False

    def get_sale_price(self, sel):
        sale_price = sel.xpath(
                "//*[@class='product-shop-info']//*[@class='special-price']//*[@class='price']/text()").extract()
        return re.sub("PKR", '', sale_price[0]) if sale_price else None

    def check_availability(self, sel):
        if sel.xpath("//*[@class='availability in-stock']//text()").extract()[1] == u'Available in stock':
            return True
        else:
            return False
