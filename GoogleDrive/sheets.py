from api import DriveAPI
import operator
import asyncio
import time
import lib
import os
import socket


class SheetsAPI(DriveAPI):

    def __init__(self, token:str, credentials:str, readonly=True, readwrite=False, file=False):
        super().__init__(token, credentials, readonly=readonly)
        self._sheets_service = None
        self._credentials = None
        self._spreadsheet = None

    @property
    def sheets_service(self):
        if self._sheets_service is None:
            self._sheets_service = self.service("sheets", "v4")
        return self._sheets_service
        
    @property
    def spreadsheet(self):
        if self._spreadsheet is None:
            self._spreadsheet = self.sheets_service.spreadsheets()
        return self._spreadsheet

    async def get_sheet(self, spreadsheetid, range, num_entries=0):
        result = self.spreadsheet.value().get(spreadsheetId=spreadsheetid, range=range)
        return await self._async_execute(result)

    async def new_sheet(self, title="Untitled Spreadsheet", retries=0):
        body = {
            "properties":{
                "title":title
            },
        }
        result = self.spreadsheet.create(body=body, fields="spreadsheetId")
        return await self._async_execute(result)
            
    async def add_sheet(self, spreadsheetId, title, header=None):
        
        sheets = (await self.spreadsheet_property(spreadsheetId))["sheets"]
        properties = operator.itemgetter("properties")
        sheets = [properties(dct)["title"] for dct in sheets]
        if title in sheets:
            raise ValueError(f"Sheet '{title}' already exists.")
    
        body = {"requests": [
                {
                "addSheet": {
                    "properties": {
                    "title": title,
                    "gridProperties": {
                        "rowCount": 1000,
                        "columnCount": 26
                    },
                    "tabColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 1.0
                    }
                }}}]}
        result = self.spreadsheet.batchUpdate(
                spreadsheetId=spreadsheetId, 
                body=body)

        return await self._async_execute(result)
    
    async def batch_update(self, spreadsheetId, _range, values):
        body = {
            "data":[
                {"majorDimension":"ROWS",
                "values":values,
                "range":_range},
            ],
            "valueInputOption":"RAW"
        }
        http = self.spreadsheet.values().batchUpdate(spreadsheetId=spreadsheetId, body=body)
        return await self._async_execute(http)

    async def append(self, spreadsheetId, _range, values):
        body = {
            "range": _range,
            "values":values,
            "majorDimension":"ROWS",
        }
        http = self.spreadsheet.values().append(spreadsheetId=spreadsheetId, range=_range, body=body, valueInputOption="RAW")
        return await self._async_execute(http)
    
    async def update(self, spreadsheetId, _range, values):
        body = {
            "range":_range,
            "values":values,
            "majorDimension":"ROWS"
        }    
        http = self.spreadsheet.values().update(spreadsheetId=spreadsheetId, range=_range, body=body)
        return await self._async_execute(http)
    
    async def spreadsheet_property(self, spreadsheetid):
        http = self.spreadsheet.get(spreadsheetId=spreadsheetid, includeGridData=False)
        return await self._async_execute(http)
    
    async def rename_sheet(self, sheet, spreadsheetId, sheetId, newname):
        body = {
            "updateSheetProperties":{
                "properties":{
                    "sheetId":sheetId,
                    "title":newname,
                },
                "fields":"title",
            }
        }
        http = self.spreadsheet.batchUpdate(spreadsheetId=spreadsheetId, body=body)
        await self._async_execute(http)

