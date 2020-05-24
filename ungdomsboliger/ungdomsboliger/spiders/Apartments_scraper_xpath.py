import scrapy
from ungdomsboliger.items.AdDepartment import AdDepartment
from ungdomsboliger.items.AdApartment import AdApartment
from ungdomsboliger.Stripper import strip_tags

class ApartmentsScraperXpath(scrapy.Spider):
    name = 'ungdomsboliger3'
    allowed_domains = ["ungdomsboligaarhus.dk"]
    start_urls = ['https://ungdomsboligaarhus.dk/user']

    def parse(self, response):
        formdata = {"name": "437876", "pass": "52545"}

        yield scrapy.FormRequest.from_response(response, formdata=formdata, clickdata={'name': 'op'}, callback=self.parse_userpage)
        #yield scrapy.Request(response, callback=self.parse_page)

    def parse_userpage(self, response):
        next_page = "https://ungdomsboligaarhus.dk/search"
        yield response.follow(next_page, callback=self.parse_page)

    def parse_page(self, response):
        for department in response.xpath('//div[@class="view-content"]/table/caption/a/@href').extract():
            yield response.follow(department, callback=self.parse_department)

    def parse_department(self, response):
        apartments = response.xpath('//div[@class="view-content"]/table/tbody/tr/@id').extract()

        info = response.xpath('//div[@class="field-items"]').extract_first()
        stripped_info = strip_tags(info)

        possible_categories = {"area": "Område:",
                               "count": "Antal boliger:",
                               "contact": "Indstilling:",
                               "administration": "Administration:",
                               "other_applicants": "Øvrige ansøgere:",
                               "other_expenses": "Øvrige udgifter:",
                               "other_info": "Yderligere informationer:",
                               "animals": "Husdyr:"
                               }

        info_categories = []
        for n in possible_categories:
            if possible_categories.get(n) in stripped_info:
                info_categories.append(n)

        info = {}
        for category1 in info_categories:
            for category2 in info_categories:
                text = stripped_info.split(possible_categories.get(category1))[1]
                if possible_categories.get(category2) in text:
                    if info.get(category1) is None or (len(info.get(category1)) > len(text.split(category2)[0]) and len(text.split(category2)[0]) != 0):
                        info[category1] = text.split(possible_categories.get(category2))[0].strip()


        yield AdDepartment(
            id=response.url.split("/")[-2],
            area=info.get("area"),
            contact=info.get("contact"),
            administration=info.get("administration"),
            other_expenses=info.get("other_expenses"),
            other_information=info.get("other_info"),
            animals=False if "ikke" in response.xpath('//strong[contains(.,"Husdyr")]/following-sibling::text()').extract_first() else True,
            images=response.xpath('//h2[contains(.,"Galleri")]/following-sibling::div//a/@href').extract(),
            apartments=apartments
        )

    def parse_apartment(self, response):
        print()


# Maps location: https://www.google.dk/maps/place/ + address
