import scrapy


class Department(scrapy.Item):
    id = scrapy.Field()
    phone = scrapy.Field()
    mail = scrapy.Field()
    animals = scrapy.Field()

    administration = scrapy.Field()
    housing_count = scrapy.Field()
    location = scrapy.Field()
    other_expenses = scrapy.Field()
    other_information = scrapy.Field()
    region = scrapy.Field()
    responsible = scrapy.Field()

    images = scrapy.Field()
    apartments = scrapy.Field()