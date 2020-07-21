import scrapy
import re


# Ctrl + ´ => Run
from ungdomsboliger.items.Department import Department


class UngdomsboligSpider(scrapy.Spider):
    name = 'ungdomsboliger'
    allowed_domains = ["ungdomsboligaarhus.dk"]
    start_urls = ['https://ungdomsboligaarhus.dk/search']

    # def parse(self, response):
    #     formdata = {"name": "437876", "pass": "52545"}
    #     yield scrapy.FormRequest.from_response(response, formdata=formdata, clickdata={'name': 'op'}, callback=self.parse_userpage)

    # def parse_userpage(self, response):
    #     next_page = "https://ungdomsboligaarhus.dk/search"
    #     yield response.follow(next_page, callback=self.parse_page)

    def parse(self, response):
        # yield response.follow(response.xpath('//div[@class="view-content"]/table/caption/a/@href').extract_first(), callback=self.parse_department)
        for department in response.xpath('//div[@class="view-content"]/table/caption/a/@href').extract():
            yield response.follow(department, callback=self.parse_department)

        # next_page = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()
        # if next_page:
        #     yield response.follow(next_page, callback=self.parse)

    def parse_department(self, response):
        def keyword_translator(keyword):
            map = {
                "administration": "administration",
                "antal boliger": "housing_count",
                "beliggenhed": "location",
                "øvrige udgifter": "other_expenses",
                "yderligere informationer": "other_information",
                "område": "region",
                "indstilling": "responsible"
            }
            return map[keyword.lower().strip().replace(":", "")]

        apartment_ids = response.xpath('//div[@class="view-content"]/table/tbody/tr/@id').extract()
        department_id = response.url.split("/")[-2]
        phone = ""
        mail = ""
        other = ""
        pets = False

        info_list = response.xpath('//div[@class="field-items"]/div//text()').extract()
        info = "\n".join([item for item in info_list if item.strip() != ""])
        if re.search(r"NB", info):
            other += re.findall("NB.*\n", info)[0]
            info = info.replace(other, "")
        if re.search(r"BEMÆRK", info):
            other += re.findall("BEMÆRK.*\n", info)[0]
            info = info.replace(other, "")

        points = response.xpath('//div[@class="field-items"]/div//b/text() | //div[@class="field-items"]/div//strong/text()').extract()
        indecies = []

        for point in points:
            if point in info:
                i = info.index(point)
                indecies.append(i)
        indecies.append(-1)

        details = {}
        for point in range(len(points)):
            start_point = len(points) - point - 1
            end_point = len(points) - point
            key = keyword_translator(points[start_point])
            res = info[indecies[start_point] + len(points[start_point]):indecies[end_point]].strip().replace(":", "")
            if key == "pets":
                pets = False if "ikke" in res.lower() else True
            elif key == "administration":
                phone = (re.findall(r"\d\d ?\d\d ?\d\d ?\d\d", info) or [""])[0]
                info = info.replace(phone, "")
                info = re.sub(r"tlf|Tlf\.?", "", info)
                mail = (re.findall(r"[a-zA-ZæøåÆØÅ\-._\d]+@[a-zA-ZæøåÆØÅ\-._\d]+\.[a-zA-ZæøåÆØÅ\-._\d]+", info) or [""])[0]
                info = info.replace(mail, info)
                info = re.sub(r"mail|Mail", "", info)
                details[key] = res.strip()
            else:
                details[key] = res

        # import pprint
        # pprint.PrettyPrinter().pprint(details)

        yield Department(
            id=department_id,
            phone=phone,
            mail=mail,
            animals=pets,

            administration=details.setdefault("administration", ""),
            housing_count=details.setdefault("housing_count", ""),
            location=details.setdefault("location", ""),
            other_expenses=details.setdefault("other_expenses", ""),
            other_information=details.setdefault("other_information", ""),
            region=details.setdefault("region", ""),
            responsible=details.setdefault("responsible", ""),

            images=response.xpath('//h2[contains(.,"Galleri")]/following-sibling::div//a/@href').extract(),
            apartments=apartment_ids
        )
        # for apartment_id in apartment_ids:
        #     yield response.follow("https://ungdomsboligaarhus.dk/apartments/" + apartment_id,
        #                           callback=self.parse_apartment,
        #                           meta={"department_id": department_id})

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
