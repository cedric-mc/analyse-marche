# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

class DvoPipeline:
    def clean_prix(self, prix_str):
        if not isinstance(prix_str, str):
            return None
        return int(prix_str) if prix_str else None

    def clean_surface(self, surface_str):
        if not isinstance(surface_str, str):
            return None
        surface_clean = re.sub(r"[^\d\.]", "", surface_str)
        return float(surface_clean) if surface_clean else None

    def clean_to_int(self, value):
        if not isinstance(value, str):
            return None
        value_clean = re.sub(r"[^\d]", "", value)
        return int(value_clean) if value_clean else None

    def process_item(self, item, spider):
        # Nettoyage du prix
        item['prix'] = self.clean_prix(item.get('prix'))

        # Nettoyage de la surface
        item['surface'] = self.clean_surface(item.get('surface'))

        # Nettoyage du nombre de chambres
        item['chambres'] = self.clean_to_int(item.get('chambres'))

        # Nettoyage du garage
        item['garage'] = self.clean_to_int(item.get('garage'))

        # Chambres, salles de bain, garage en int
        for col in ['chambres', 'salles_bain', 'garage']:
            value = item.get(col)
            try:
                item[col] = int(value)
            except (TypeError, ValueError):
                item[col] = None

        # Calcul prix au m² si possible
        if item['prix'] is not None and item['surface'] is not None and item['surface'] != 0:
            item['prix_m2'] = item['prix'] / item['surface']
        else:
            item['prix_m2'] = None

        return item

