from datetime import datetime
from pathlib import Path
import GoogleDrive
import os
import json
import lib
import asyncio
import sys
import collections

async def main(month):
    try:
        month = int(month)
    except:
        print(f"Invalid input {month}")
        exit(1)
    
    configpath = os.path.join(str(Path.home()), ".hwk", "config.json")
    with open(configpath, "r") as fp:
        SALES_SHEET = json.load(fp)["saleslog id"]

    api = GoogleDrive.SheetsAPI(lib.TOKEN, lib.CREDENTIALS)
    properties = (await api.spreadsheet_property(SALES_SHEET))["sheets"]
    titles = [
        sheet["properties"]["title"] for sheet in properties 
    ]

    ranges = [
        f"'{title}'!A2:F" for title in titles 
            if datetime.strptime(title, "%m-%d-%y").month == month
    ]

    counter = collections.Counter()
    for _range in ranges:
        result = (await api.get_sheet(SALES_SHEET, _range))["values"]
        for timestamp, total, subtotal, tax, payment_type, items in result:
            total = int(total)
            counter.update({payment_type.strip():total})
    
   
    total = 0
    for key in counter:
        if key == "Invoice":
            name = "Sale Barn"
        else:
            name = key
        print(f"{name}: " + "$ {:.2f}".format(counter[key] / 100))
        total += counter[key]
    
    print("TOTAL: $ {:.2f}".format(total / 100))

    
    
    


if __name__ == "__main__":
    try:
        month_input =sys.argv[1]
    except:
        print("no input month")
    else:
        asyncio.run(main(month_input))