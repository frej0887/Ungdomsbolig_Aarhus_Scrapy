import scrapy


class AdApartment(scrapy.Item):
    department = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    fixtures = scrapy.Field()
    kitchen = scrapy.Field()
    bath_toilet = scrapy.Field()
    TV_wifi = scrapy.Field()
    laundry = scrapy.Field()
    other_fac_out = scrapy.Field()
    other_fac_in = scrapy.Field()
    other_information = scrapy.Field()