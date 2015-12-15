# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Garment(scrapy.Item):
    item_code = scrapy.Field()
    item_name = scrapy.Field()
    item_price = scrapy.Field()
    source_url = scrapy.Field()
    item_image_url = scrapy.Field()
    item_second_image_url = scrapy.Field()
    item_third_image_url = scrapy.Field()
    item_secondary_image_urls = scrapy.Field()
    item_brand_id = scrapy.Field()
    item_category_name = scrapy.Field()
    item_description = scrapy.Field()
    item_is_available = scrapy.Field()
    item_is_on_sale = scrapy.Field()
    item_sale_price = scrapy.Field()
