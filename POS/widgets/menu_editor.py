from lib import MenuType
from lib import MENUDATA
from lib import MenuItem
import logging as log
import sys
import json

logger = log.getLogger(__name__)
logger.setLevel(log.DEBUG)

output = log.StreamHandler(stream=sys.stdout)
output.setFormatter(
        log.Formatter("%(name)s - %(levelname)s - %(funcName)s - %(message)s"))
logger.addHandler(output)


class MenuEditor(metaclass=MenuType):

    def __init__(self, filename, itemclass=None):
        if itemclass is None:
            itemclass = MenuItem
        self.ItemClass = itemclass

        self.filename = filename
        self.all = []
        for category in MenuEditor.categories:
            self.all.extend(MenuEditor.category(category))

    def add_item(self, category, name, price, options):
        if (category, name) not in self.all:
            self.all.append(self.ItemClass(
                    category, name, price, options))
        logger.info(f"Added: {self.ItemClass(category, name, price, options)}")

    def remove_item(self, category, name):
        if (category, name) in self.all:
            self.all.pop(self.all.index((category, name)))
        logger.info(f"Removed: {(category, name)}")

    def edit_item(self, category, name, price, options):
        item = self.ItemClass(category, name, price, options)
        previous = self.all.pop(self.all.index((category, name)))
        self.all.append(item)
        logger.info(f"{previous} -> {item}")

    def to_dict(self):
        result = {"menu":{}, "config":{}}
        for item in self.all:
            result["menu"][item.category] = dict()

        for item in self.all:
            result["menu"][item.category][item.name] = dict()
        
        for item in self.all:
            result["menu"][item.category][item.name]["Price"] = item.price
            result["menu"][item.category][item.name]["Options"] = item.options

        result["config"]["Sides Included"] = getattr(MenuEditor, "include_sides")
        result["config"]["Drinks Included"] = getattr(MenuEditor, "include_drinks")
        result["config"]["Two Sides"] = getattr(MenuEditor, "two_sides")
        result["config"]["No Addons"] = getattr(MenuEditor, "no_addons")
        return result

    def to_csv(self):
        return self.__repr__()

    def save(self, csv=False):
        if csv:
            with open(self.filename, "w") as fp:
                fp.write(self.to_csv())
        else:
            with open(self.filename, "w") as fp:
                json.dump(fp, self.to_dict())
    
    @classmethod
    def load(cls, new_menu):
        items = new_menu["menu"]
        config = new_menu["config"]

        for category in items:
            cls.menu[category] = items[category] # pylint: disable=E1101
        
        for conf in config:
            cls.config = config[conf]
        logger.info("Loaded new menu")