import scrapy
from ungdomsboliger.items.AdDepartment import AdDepartment
from ungdomsboliger.items.AdApartment import AdApartment
from ungdomsboliger.Stripper import strip_tags


class ApartmentsScraperXpath(scrapy.Spider):
    name = 'ungdomsboliger3'
    allowed_domains = ["ungdomsboligaarhus.dk"]
    start_urls = ['https://ungdomsboligaarhus.dk/search']

    # def parse(self, response):
    #     formdata = {"name": "437876", "pass": "52545"}
    #     yield scrapy.FormRequest.from_response(response, formdata=formdata, clickdata={'name': 'op'}, callback=self.parse_userpage)

    # def parse_userpage(self, response):
    #     next_page = "https://ungdomsboligaarhus.dk/search"
    #     yield response.follow(next_page, callback=self.parse_page)

    def parse(self, response):
        for department in response.xpath('//div[@class="view-content"]/table/caption/a/@href').extract():
            yield response.follow(department, callback=self.parse_department)

        next_page = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_department(self, response):
        apartment_ids = response.xpath('//div[@class="view-content"]/table/tbody/tr/@id').extract()
        department_id = response.url.split("/")[-2]
        info = response.xpath('//div[@class="field-items"]').extract_first()
        stripped_info = strip_tags(info)

        animals_raw = response.xpath('//strong[contains(.,"Husdyr")]/following-sibling::text()').extract_first()
        animals = False if animals_raw is None else (False if "ikke" in animals_raw else True)
        info = doStuff(stripped_info)

        yield AdDepartment(
            id=department_id,
            area=info.get("area"),
            contact=info.get("contact"),
            administration=info.get("administration"),
            other_expenses=info.get("other_expenses"),
            other_information=info.get("other_info"),
            animals=animals,
            images=response.xpath('//h2[contains(.,"Galleri")]/following-sibling::div//a/@href').extract(),
            apartments=apartment_ids
        )
        for apartment_id in apartment_ids:
            yield response.follow("https://ungdomsboligaarhus.dk/apartments/" + apartment_id,
                                  callback=self.parse_apartment,
                                  meta={"department_id": department_id})

    def parse_apartment(self, response):
        info = response.xpath('//div[@class="field-items"]').extract_first()
        stripped_info = strip_tags(info)

        info = doStuff(stripped_info)

        if info.get("TV_wifi"):
            tv_wifi = info.get("TV_wifi")
        elif info.get("tv") and info.get("wifi"):
            tv_wifi = info.get("tv") + " " + info.get("wifi")
        elif info.get("tv"):
            tv_wifi = info.get("tv")
        elif info.get("wifi"):
            tv_wifi = info.get("wifi")
        else:
            tv_wifi = None

        # yield info
        yield AdApartment(
            id=response.url.split("/")[-1],
            rooms=info.get("rooms"),
            department=response.meta.get("department_id"),
            floor=info.get("floor_type"),
            fixtures=info.get("fixtures"),
            kitchen=info.get("kitchen"),
            bath_toilet=info.get("bath_toilet"),
            TV_wifi=tv_wifi,
            laundry=info.get("laundry"),
            other_fac_out=info.get("other_fac_out"),
            other_fac_in=info.get("other_fac_in"),
            other_information=info.get("other_information"),
        )


# Maps location: https://www.google.dk/maps/place/ + address

def doStuff(stripped_info):
    possible_categories = {"Område": "area",
                           "Beliggenhed": "address",
                           "Mail": "mail",
                           "Antal boliger": "count",
                           "Indstilling": "contact",
                           "Administration": "administration",
                           "Øvrige ansøgere": "other_applicants",
                           "Øvrige udgifter": "other_expenses",
                           "Yderligere informationer": "other_info",
                           "Husdyr": "animals",
                           "Gulvbelægning": "floor_type",
                           "Inventar": "fixtures",
                           "Køkken": "kitchen",
                           "Bad/toilet": "bath_toilet",
                           "TV og internet": "TV_wifi",
                           "Internet": "wifi",
                           "TV": "tv",
                           "Vaskeri": "laundry",
                           "Fælles faciliteter ude": "other_fac_out",
                           "Fælles faciliteter inde": "other_fac_in",
                           "Øvrige fælles faciliteter": "other_facilities",
                           "Supplerende oplysninger": "other_information",
                           }
    meh = []
    for eh in stripped_info.split("\n"):
        if eh.strip() != "":
            meh.append(eh.strip())
    dict = {}
    if "Supplerende oplysninger" in meh:
        index = meh.index("Supplerende oplysninger")
        dict["other_information"] = " ".join(meh[index + 1:])

    stuff = ""
    name = ""
    for eh in meh:
        if ":" in eh:
            if stuff != "":
                if stuff.strip() != "" and name.strip() == "":
                    name = "rooms"
                dict[name] = stuff
            stuff = ""
            index = eh.index(":")
            name = possible_categories.setdefault(eh[:index], "other")
            stuff = stuff + eh[index + 1:]
        else:
            stuff = stuff + eh
    return dict
