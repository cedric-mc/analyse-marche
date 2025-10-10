from time import sleep
import scrapy
import os
import json


class FrenchImmobilierSpider(scrapy.Spider):
    name = "french_immobilier"
    allowed_domains = ["etreproprio.com"]
    start_urls = [
        "https://www.etreproprio.com/maison-a-vendre",
        "https://www.etreproprio.com/appartement-a-vendre",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filters_env = os.getenv("SCRAPING_FILTERS", "{}")
        self.filters = json.loads(filters_env)
        self.log(f"Filtres appliqués : {self.filters}")

    # ===============================
    # 1️⃣ Page type → département
    # ===============================
    def parse(self, response):
        self.log(f"📍 Type de bien : {response.url}")
        # Chaque section principale contient des liens vers les départements
        departements = response.css("section.ep-cla-key-sec a::attr(href)").getall()
        for lien in departements:
            if lien.startswith("/"):
                lien = "https://www.etreproprio.com" + lien
            yield scrapy.Request(lien, callback=self.parse_departement)

    # ===============================
    # 2️⃣ Page département → villes
    # ===============================
    def parse_departement(self, response):
        self.log(f"🏛 Département : {response.url}")
        villes = response.css("div.ep-cla-dir-top-cities a::attr(href)").getall()
        for lien in villes:
            if lien.startswith("/"):
                lien = "https://www.etreproprio.com" + lien
            yield scrapy.Request(lien, callback=self.parse_ville)

    # ===============================
    # 3️⃣ Page ville → annonces
    # ===============================
    def parse_ville(self, response):
        self.log(f"🏘 Ville : {response.url}")
        annonces = response.css("div.ep-cla-key-list a::attr(href)").getall()
        for lien in annonces:
            if lien.startswith("/"):
                lien = "https://www.etreproprio.com" + lien
            yield scrapy.Request(lien, callback=self.parse_liste_annonces)

    # ===============================
    # 4️⃣ Liste d'annonces → chaque annonce
    # ===============================
    def parse_liste_annonces(self, response):
        self.log(f"📄 Liste d’annonces : {response.url}")

        for annonce in response.css("div.ep-search-list-wrapper a::attr(href)").getall():
            if "immobilier-" in annonce:
                full_link = annonce if annonce.startswith("http") else "https://www.etreproprio.com" + annonce
                image_principale = response.css("img::attr(src)").get()
                yield scrapy.Request(
                    full_link,
                    callback=self.parse_annonce,
                    meta={"image_principale": image_principale, "url_annonce": full_link},
                )

        # Pas de pagination ici : toutes les annonces sont accessibles par ville

    # ===============================
    # 5️⃣ Détail annonce
    # ===============================
    def parse_annonce(self, response):
        image_principale = response.meta.get("image_principale")
        url_annonce = response.meta.get("url_annonce")

        images_page = response.css("div.ep-tiles-photos img::attr(src)").getall()

        options = {
            "parking": response.css("div.ep-features img::attr(alt)").re_first("parking"),
            "jardin": response.css("div.ep-features img::attr(alt)").re_first("jardin"),
            "balcon_terrasse": response.css("div.ep-features img::attr(alt)").re_first("balcon|terrasse"),
            "piscine": response.css("div.ep-features img::attr(alt)").re_first("piscine"),
            "ascenseur": response.css("div.ep-features img::attr(alt)").re_first("ascenseur"),
            "acces_handicape": response.css("div.ep-features img::attr(alt)").re_first("accès handicapé"),
        }

        titre = response.css("h1.annonce-immobilier::text").get()
        type_bien = response.css(
            'div.ep-breadcrumb-cla-dir li:nth-child(2) span[itemprop="name"]::text'
        ).get()
        prix = response.css("div.ep-price::text").get()
        surface = response.css("div.ep-area::text").get()
        localisation = response.css("div.ep-loc::text").get()

        # --- 💡 Filtres
        f = self.filters
        if f.get("type") and all(t.lower() not in (type_bien or "").lower() for t in f["type"]):
            return
        if f.get("ville") and not any(v.lower() in (localisation or "").lower() for v in f["ville"]):
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

        # --- Résultat final
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
            **options,
            "agence": response.css("div.ep-name a::text").get(),
        }
