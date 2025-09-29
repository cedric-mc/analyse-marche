import scrapy
import json

class FrenchImmobilierSpider(scrapy.Spider):
    name = 'french_immobilier'
    allowed_domains = ['french-immobilier.com']
    start_urls = ['https://french-immobilier.com/property_group/a-vendre/']

    results = []

    def parse(self, response):
        for annonce in response.css('div.sc_property_item'):
            prix = annonce.css('span.property_price_box_price::text').get()
            prix_sign = annonce.css('span.property_price_box_sign::text').get(default='€')
            surface = annonce.css('span.icon-building113::text').get()
            chambres = annonce.css('span.icon-bed::text').get()
            salles_bain = annonce.css('span.icon-bath::text').get()
            garage = annonce.css('span.icon-warehouse::text').get()
            
            item = {
                'titre': annonce.css('div.sc_property_description::text').get(),
                'prix': f"{prix} {prix_sign}" if prix else None,
                'surface': surface,
                'chambres': chambres,
                'salles_bain': salles_bain,
                'garage': garage,
                'ville': annonce.css('div.sc_property_title_address_1 a::text').get(),
                'quartier': annonce.css('div.sc_property_title_address_2::text').get(),
                'lien': annonce.css('div.sc_property_image a::attr(href)').get(),
            }
            self.results.append(item)
            yield item

        # Pagination
        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
