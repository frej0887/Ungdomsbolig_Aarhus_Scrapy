import scrapy


class AdDepartment(scrapy.Item):
    id = scrapy.Field()
    area = scrapy.Field()
    contact = scrapy.Field()
    administration = scrapy.Field()
    other_expenses = scrapy.Field()
    other_information = scrapy.Field()
    animals = scrapy.Field()
    images = scrapy.Field()
    apartments = scrapy.Field()