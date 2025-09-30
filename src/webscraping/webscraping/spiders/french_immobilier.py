import scrapy
import json

class FrenchImmobilierSpider(scrapy.Spider):
    name = 'french_immobilier'
    allowed_domains = ['french-immobilier.com']
    start_urls = ['https://french-immobilier.com/property_group/a-vendre/']

    results = []

    def parse(self, response):
        for annonce in response.css('div.sc_property_item'):
            item = {
                'titre': annonce.css('div.sc_property_description::text').get(),
                'prix': annonce.css('span.property_price_box_price::text').get(),
                'surface': annonce.css('span.icon-building113::text').get().replace("m²", "").strip(),
                'chambres': annonce.css('span.icon-bed::text').get(),
                'salles_bain': annonce.css('span.icon-bath::text').get(),
                'garage': annonce.css('span.icon-warehouse::text').get(),
                'ville': annonce.css('div.sc_property_title_address_1 a::text').get(),
                'quartier': annonce.css('div.sc_property_title_address_2::text').get(),
                'lien': annonce.css('div.sc_property_image a::attr(href)').get(),
                'image': annonce.css('img.wp-post-image img::attr(src)').get()
            }
            self.results.append(item)
            yield item

        # Pagination : chercher le bouton "suivant"
        next_page = response.css('a.pager_next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
