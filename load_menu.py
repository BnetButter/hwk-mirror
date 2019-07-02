import GoogleDrive
import lib
import json
import asyncio


class MenuLogger(metaclass=lib.MenuType):
    
    def __init__(self):
        self.api = GoogleDrive.SheetsAPI(lib.TOKEN, lib.CREDENTIALS)

    async def download(self):
        properties = await self.api.spreadsheet_property(lib.MENU_SPREADSHEET_ID)
        menu_config = (await self.api.get_sheet(lib.MENU_SPREADSHEET_ID, "'menuconfig'!A1:B"))["values"]
        menu_config = {
            k: eval(v)
            for k, v in menu_config
        }
        type(self).menu_config = menu_config
        
        categories = [info["properties"]["title"]
                for info in properties["sheets"]
                    if info["properties"]["title"] != "menuconfig"]
        menu_items = {}
        for category in categories:
            category_dct = {}
            result = (await self.api.get_sheet(lib.MENU_SPREADSHEET_ID, f"'{category}'!A2:E"))["values"]
            for name, price, options, alias, hidden in result:
                price = eval(price)
                options = eval(options)
                if alias == "None":
                    alias = None
                hidden = eval(hidden)
                category_dct[name] = {"Price":price,"Options":options,"alias":alias,"hidden":hidden}
            
            menu_items[category] = category_dct
    
        type(self).menu_items = menu_items
        with open(lib.MENUPATH, "w") as fp:
            json.dump({"menu":menu_items, "config":menu_config}, fp, indent=4)

    async def update(self):
        menu_config = type(self).menu_config
        menu_items = type(self).menu_items
        config_data = list()
        config_range = "'menuconfig'!A1:B"
        for config in menu_config:
            Acolumn = config
            Bcolumn = str(menu_config[config])
            config_data.append([Acolumn, Bcolumn])
        
        for category in menu_items:
            category_range = f"'{category}'!A2:E"
            category_data = list()
            for item in menu_items[category]:
                info = menu_items[category][item]
                category_data.append([item, info["Price"], str(info["Options"]), str(info["alias"]), info["hidden"]])
            await self.api.batch_update(lib.MENU_SPREADSHEET_ID, category_range, category_data)
    
        await self.api.batch_update(lib.MENU_SPREADSHEET_ID, config_range, config_data)
        

    async def upload_local(self):
        with open(lib.MENUPATH, "r") as fp:
            menuinfo = json.load(fp)
            menu = menuinfo["menu"]
            menu_config = menuinfo["config"]
        try:
            await api.add_sheet(lib.MENU_SPREADSHEET_ID, "menuconfig")
            data = list()
            for config in menu_config:
                Acolumn = config
                Bcolumn = str(menu_config[config])
                data.append([Acolumn, Bcolumn])
            await api.append(lib.MENU_SPREADSHEET_ID, "'menuconfig'!A1:B", data)
        except:
            ...
        headers = ["Name", "Price", "Options", "alias", "hidden"]
        for category in menu:
            data = [headers]
            for item in menu[category]:
                info = menu[category][item]
                data.append([item, info["Price"], str(info["Options"]), str(info["alias"]), info["hidden"]])
            try:
                await api.add_sheet(lib.MENU_SPREADSHEET_ID, category)
                await api.append(lib.MENU_SPREADSHEET_ID, f"'{category}'!A1:E", data)
            except:
                continue


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    menulogger = MenuLogger()
    loop.run_until_complete(menulogger.update())