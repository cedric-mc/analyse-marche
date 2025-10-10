from time import sleep
import scrapy
import os
import json

class FrenchImmobilierSpider(scrapy.Spider):
    name = 'french_immobilier'
    allowed_domains = ["etreproprio.com"]
    start_urls = ["https://www.etreproprio.com/annonces"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Charger les filtres envoyés par Streamlit
        filters_env = os.getenv("SCRAPING_FILTERS", "{}")
        self.filters = json.loads(filters_env)
        self.log(f"Filtres appliqués : {self.filters}")

    def parse(self, response):
        """
        Parse la page des résultats (liste des annonces).
        Récupère les infos de base + lien vers la fiche annonce.
        """
        annonces = response.css("div.ep-search-list-wrapper a")
        for annonce in annonces:
            lien = annonce.css("a::attr(href)").get()

            # Vérifier qu’on a bien un lien d’annonce
            if lien and "https://www.etreproprio.com/immobilier-" in lien:
                image_principale = annonce.css("img::attr(src)").get()

                # Passer l’image principale en meta pour l’envoyer à parse_annonce
                yield response.follow(
                    lien,
                    callback=self.parse_annonce,
                    meta={"image_principale": image_principale, "url_annonce": lien},
                )

        # Pagination
        next_page = response.css("a.ep-nav-link-next::attr(href)").get()
        if next_page:
            sleep(5)
            yield response.follow(next_page, callback=self.parse)

    def parse_annonce(self, response):
        """
        Parse la fiche détaillée d'une annonce.
        """
        image_principale = response.meta.get("image_principale")
        url_annonce = response.meta.get("url_annonce")

        # Récupérer toutes les images présentes sur la page
        images_page = response.css("div.ep-tiles-photos img::attr(src)").getall()

        # Récupérer les options (parking, jardin, balcon/terrasse, piscine, ascenseur, accès handicapé)
        options = {
            "parking": response.css("div.ep-features img::attr(alt)").re_first('parking'),
            "jardin": response.css("div.ep-features img::attr(alt)").re_first('jardin'),
            "balcon_terrasse": response.css("div.ep-features img::attr(alt)").re_first('balcon/terrasse'),
            "piscine": response.css("div.ep-features img::attr(alt)").re_first('piscine'),
            "ascenseur": response.css("div.ep-features img::attr(alt)").re_first('ascenseur'),
            "acces_handicape": response.css("div.ep-features img::attr(alt)").re_first('accès handicapé'),
        }

        titre = response.css("h1.annonce-immobilier::text").get()
        type_bien = response.css('div.ep-breadcrumb-cla-dir li:nth-child(2) span[itemprop="name"]::text').get()
        prix = response.css("div.ep-price::text").get()
        surface = response.css("div.ep-area::text").get()
        localisation = response.css("div.ep-loc::text").get()

        # --- 💡 Application des filtres
        f = self.filters
        if f.get("type") and all(t.lower() not in type_bien.lower() for t in f["type"]):
            return
        if f.get("ville") and not any(v.lower() in localisation.lower() for v in f["ville"]):
            return
        if f.get("prix_min") or f.get("prix_max"):
            import re
            prix_num = re.sub(r"[^\d]", "", prix or "0")
            if prix_num:
                prix_val = int(prix_num)
                if prix_val < f.get("prix_min", 0) or prix_val > f.get("prix_max", 10**9):
                    return
        if f.get("surface_min") or f.get("surface_max"):
            import re
            surf_num = re.sub(r"[^\d]", "", surface or "0")
            if surf_num:
                surf_val = int(surf_num)
                if surf_val < f.get("surface_min", 0) or surf_val > f.get("surface_max", 10**6):
                    return

        # --- Si l’annonce passe les filtres, on la garde
        yield {
            "titre": titre,
            "type": type_bien,
            "lien": url_annonce,
            "prix": prix,
            "surface": surface,
            "surface_terrain": response.css("span.dtl-main-surface-terrain::text").get(),
            "pieces": response.css("div.ep-room::text").get(),
            "dpe": response.css("div.dpe-container div.dpe-letter.selected::text").get(),
            "ges": response.css("div.ges-container div.ges-letter.selected::text").get(),
            "localisation": localisation,
            "image_principale": image_principale,
            "images_page": images_page,
            "parking": options.get("parking"),
            "jardin": options.get("jardin"),
            "balcon_terrasse": options.get("balcon_terrasse"),
            "piscine": options.get("piscine"),
            "ascenseur": options.get("ascenseur"),
            "acces_handicape": response.css("div.ep-features img::attr(alt)").re_first('accès handicapé'),
            "agence": response.css("div.ep-name a::text").get()
        }