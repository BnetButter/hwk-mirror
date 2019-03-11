from lib import MenuType
from lib import MENUDATA
from lib import MenuItem
import json

class MenuEditor(metaclass=MenuType):

    def __init__(self, filename, itemclass=None):
        if itemclass is None:
            itemclass = MenuItem
        self.ItemClass = itemclass

        self.filename = filename
        self.all = [
            MenuItem(*MenuEditor.category(category)) for category in getattr(MenuEditor, "menu")]

    def add_item(self, category, name, price, options):
        if (category, name) not in self.all:
            self.all.append(self.ItemClass(
                    category, name, price, options))
    
    def remove_item(self, category, name):
        if (category, name) in self.all:
            self.all.pop(self.all.index((category, name)))

    def edit_item(self, category, name, price, options):
        item = self.ItemClass(category, name, price, options)
        self.all.pop(self.all.index((category, name)))
        self.all.append(item)

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