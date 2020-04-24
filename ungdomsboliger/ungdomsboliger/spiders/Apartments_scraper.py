import scrapy
import re


# Ctrl + ´ => Run

class UngdomsboligSpider(scrapy.Spider):
    name = 'ungdomsboliger'

    start_urls = [
        'https://ungdomsboligaarhus.dk/search?page=0',
    ]

    def parse(self, response):
        '''page = response.url.split('=')[-1]
        filename = '%s.html' %page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)'''
        for department in response.css('table.views-table'):
            apartment_set = []
            department_name = str(department.css("caption").css("a").css("div::text").get()).strip()
            departments = department.css("tbody").css("tr")
            for row in departments:
                # Backup: lav en liste og grupér senere
                if departments.index(row) == len(departments) - 1:
                    apartment_set.append(row)
                if re.search("id=", row.css("tr").get()) or departments.index(row) == len(departments) - 1:
                    if apartment_set:
                        ret = self.doStuff(apartment_set)
                        yield {
                            "ID": ret["id"],
                            'department': department_name,
                            "address": ret["address"],
                            "rooms": ret["rooms"],
                            "rent": ret["rent"],
                            "downpay": ret["downpay"],
                            "own fac": ret["ofac"],
                            "others": ret["lines"]
                        }
                    apartment_set = []
                apartment_set.append(row)

    def doStuff(self, ls):
        tds = ls[0].css("td")

        ID = ls[0].css("::attr(id)").get()
        rooms_outer = str(tds[1].css("a::text").get().strip())
        address = str(tds[1].css("a::text").getall()[1].strip())

        for i in range(len(address)):
            address = address.replace(" ,", ",")
        rent_outer = str(tds[3].css("::text").get()).strip().replace(".", "").replace(",", ".")
        downpay_outer = str(tds[4].css("::text").get()).strip().replace(".", "").replace(",", ".")

        lines = []
        tds = [ls[i].css("td") for i in range(1, len(ls))]
        for row in tds:
            if tds.index(row) == 0:
                ofac = str([eh.css("::attr(title)").get() for eh in row[1].css('div[class="facilities_own"]').css("img")])
                #print("Own facilities: " + ofac)
            count = row[2].css("::text").get()
            wait = row[3].css("::text").get()
            area = str(row[4].css("::text").get()).replace(",", ".")
            rent = str(row[5].css("::text").get()).replace(".", "").replace(",", ".")
            downpay = str(row[6].css("::text").get()).replace(".", "").replace(",", ".")
            floor_plan = row[7].css("a::attr(href)").get(default='None')

            lines.append({
                "count": count,
                "wait": wait,
                "area": area,
                "rent": rent,
                "downpay": downpay,
                "floor_plan": floor_plan
                })

        return {
            "id": ID,
            "rooms": rooms_outer,
            "address": address,
            "rent": rent_outer,
            "downpay": downpay_outer,
            "ofac": ofac,
            "lines": lines
        }
